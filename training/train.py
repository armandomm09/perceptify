from ultralytics import YOLO

def train_from_scratch(model_path, dataset_location, n_epochs=50, n_imgsz = 640, n_device="mps"):
    model = YOLO(model_path)
    results = model.train(data=f"{dataset_location}/data.yaml", epochs=n_epochs, imgsz=n_imgsz, device=n_device)
    
import torch

def continue_training(last_pt_path):
    model = YOLO(last_pt_path)
    model.train(resume=True, device="mps", batch=8, imgsz=416)
    torch.cuda.empty_cache() 

    