# detect cuda
import os


def detect_cuda():
    # run some code on GPU and check if it runs
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False



if __name__ == '__main__':
    print(detect_cuda())