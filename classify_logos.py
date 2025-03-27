import os
import shutil
import torch
import clip
from PIL import Image, ImageOps
from tqdm import tqdm
import numpy as np
import hdbscan
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics.pairwise import cosine_similarity
from skimage.metrics import structural_similarity as ssim
from logger import log_event
from config import LOGO_DIR,CLASSIFIED_LOGOS_FOLDER


USE_CUDA = torch.cuda.is_available()
device = "cuda" if USE_CUDA else "cpu"
log_event("Start classify_logos.py", "Started")
log_event("Start classifying logos", "Started")
log_event("Model CLIP", "Loading")
model, preprocess_clip = clip.load("ViT-B/32", device=device)


def extract_features(img_path):

    try:
        image = Image.open(img_path).convert("RGB")
        image = ImageOps.pad(image, (224, 224), method=Image.BICUBIC, color=(255, 255, 255))
        image = preprocess_clip(image).unsqueeze(0).to(device)
        with torch.no_grad():
            features = model.encode_image(image)
            features /= features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().flatten()
    except Exception as e:
        log_event("Extract Features", "Error", f"{img_path}: {e}")
        return None


def compute_ssim_score(img1_path, img2_path):
    try:
        img1 = Image.open(img1_path).resize((224, 224)).convert("L")
        img2 = Image.open(img2_path).resize((224, 224)).convert("L")
        return ssim(np.array(img1), np.array(img2))
    except Exception:
        return 0.0


def save_grouped_images(paths, labels, prefix="group_"):
    for idx in set(labels):
        folder = os.path.join(CLASSIFIED_LOGOS_FOLDER, f"{prefix}{idx}" if idx != -1 else "ungrouped")
        os.makedirs(folder, exist_ok=True)
    for path, label in zip(paths, labels):
        folder = os.path.join(CLASSIFIED_LOGOS_FOLDER, f"{prefix}{label}" if label != -1 else "ungrouped")
        dst = os.path.join(folder, os.path.basename(path))
        try:
            shutil.copy(path, dst)
        except Exception as e:
            log_event("Save Grouped Image", "Error", f"{path}: {e}")


def group_by_ssim(image_paths, threshold=0.85):
    log_event("SSIM Grouping", "Started")
    groups = []
    ungrouped = set(image_paths)

    while ungrouped:
        ref = ungrouped.pop()
        group = [ref]
        to_check = list(ungrouped)
        for other in to_check:
            score = compute_ssim_score(ref, other)
            if score >= threshold:
                group.append(other)
                ungrouped.remove(other)
        groups.append(group)
    log_event("SSIM Grouping", "Completed")
    return groups


def group_logos():
    log_event("Group Logos", "Started")
    os.makedirs(CLASSIFIED_LOGOS_FOLDER, exist_ok=True)
    files = [f for f in os.listdir(LOGO_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    paths = [os.path.join(LOGO_DIR, f) for f in files]

    log_event("Extract Embeddings", "Started", f"{len(paths)} images")
    vectors, valid_paths = [], []

    for path in tqdm(paths):
        vec = extract_features(path)
        if vec is not None:
            vectors.append(vec)
            valid_paths.append(path)

    if not vectors:
        log_event("Embedding Extraction", "Error", "No valid vectors extracted.")
        return

    vectors_np = np.vstack(vectors)

    log_event("Cosine Distance Matrix", "Computing")
    distance_matrix = 1 - cosine_similarity(vectors_np)

    log_event("Clustering HDBSCAN", "Running")
    clusterer = hdbscan.HDBSCAN(metric='precomputed', min_cluster_size=3, min_samples=2, prediction_data=True)
    hdb_labels = clusterer.fit_predict(distance_matrix.astype(np.float64))

    final_labels = np.array(hdb_labels)
    current_max = final_labels.max() + 1 if len(final_labels) > 0 else 0

    log_event("HDBSCAN Results", "Done", f"Groups: {len(set(hdb_labels)) - (1 if -1 in hdb_labels else 0)}, Ungrouped: {np.sum(hdb_labels == -1)}")

    if -1 in final_labels:
        log_event("DBSCAN Fallback", "Running")
        ungrouped_indices = np.where(final_labels == -1)[0]
        ungrouped_vecs = vectors_np[ungrouped_indices]
        dbscan = DBSCAN(eps=0.15, min_samples=1, metric="cosine")
        db_labels = dbscan.fit_predict(ungrouped_vecs)
        db_labels_offset = [l + current_max for l in db_labels]
        final_labels[ungrouped_indices] = db_labels_offset
        current_max = max(final_labels) + 1

        if -1 in final_labels:
            log_event("SSIM Fallback", "Running")
            still_ungrouped_indices = np.where(final_labels == -1)[0]
            still_ungrouped_paths = [valid_paths[i] for i in still_ungrouped_indices]
            ssim_groups = group_by_ssim(still_ungrouped_paths, threshold=0.85)
            for group in ssim_groups:
                for p in group:
                    i = valid_paths.index(p)
                    final_labels[i] = current_max
                current_max += 1

    log_event("Saving Grouped Images", "Started")
    save_grouped_images(valid_paths, final_labels, prefix="group_")
    log_event("Group Logos", "Completed", f"Saved in: {CLASSIFIED_LOGOS_FOLDER}")
    log_event("End classify_logos.py", "Ended")

