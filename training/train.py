from ultralytics import YOLO

def train_from_scratch(model_path, dataset_location, n_epochs=50, n_imgsz = 640, n_device="mps"):
    model = YOLO(model_path)
    results = model.train(data=f"{dataset_location}/data.yaml", epochs=n_epochs, imgsz=n_imgsz, device=n_device)
    
import torch

def continue_training(last_pt_path):
    model = YOLO(last_pt_path)
    model.train(resume=True, device="mps", batch=8, imgsz=416)
    torch.cuda.empty_cache() 

    
# from tool import darknet2pytorch
# import torch

# # load weights from darknet format
# model = darknet2pytorch.Darknet('path/to/cfg/yolov4-416.cfg', inference=True)
# model.load_weights('path/to/weights/yolov4-416.weights')

# # save weights to pytorch format
# torch.save(model.state_dict(), 'path/to/save/yolov4-pytorch.pth')

# # reload weights from pytorch format
# model_pt = darknet2pytorch.Darknet('path/to/cfg/yolov4-416.cfg', inference=True)
# model_pt.load_state_dict(torch.load('path/to/save/yolov4-pytorch.pth'))