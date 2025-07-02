import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

# --- 全局变量，用于存储加载后的模型和类别，避免重复加载 ---
MODEL = None
CLASS_NAMES = None

# --- 常量定义 ---
# 获取当前文件所在的目录，并拼接模型和类别文件的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model/garbage_classifier_resnet18.pth')
CLASS_NAMES_FILE = os.path.join(BASE_DIR, 'class_names.txt')


def _load_model_and_classes():
    """
    一个内部函数，用于加载模型和类别名称到全局变量。
    此函数只在第一次需要时执行。
    """
    global MODEL, CLASS_NAMES

    # 检查文件是否存在
    if not os.path.exists(CLASS_NAMES_FILE):
        raise FileNotFoundError(f"类别名称文件未找到: {CLASS_NAMES_FILE}")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"模型文件未找到: {MODEL_PATH}")

    # 1. 加载类别名称
    with open(CLASS_NAMES_FILE, 'r', encoding='utf-8') as f:
        CLASS_NAMES = [line.strip() for line in f.readlines()]

    # 2. 定义与训练时完全相同的模型架构
    model_instance = models.resnet18(weights=None)
    num_ftrs = model_instance.fc.in_features
    model_instance.fc = nn.Linear(num_ftrs, len(CLASS_NAMES))

    # 3. 加载已经训练好的模型权重
    # map_location=torch.device('cpu') 确保模型即使在没有GPU的服务器上也能运行
    checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
    model_instance.load_state_dict(checkpoint['model_state_dict'])
    model_instance.eval()  # 切换到评估模式

    MODEL = model_instance
    # print("--- 图像识别模型和类别已成功加载到内存。 ---")


def _preprocess_image(image_path):
    """
    对单个图片进行预处理，使其符合模型输入要求。
    与验证集的预处理方式保持一致。
    """
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)  # 增加一个批次维度


def _predict(model, input_tensor, class_names):
    """
    使用加载好的模型进行预测。
    """
    with torch.no_grad():
        output = model(input_tensor)
        # 使用 softmax 将输出转换为概率分布
        probabilities = torch.nn.functional.softmax(output[0], dim=0)

        # 获取概率最高的预测结果
        top_prob, top_idx = torch.topk(probabilities, 1)

        # 从索引映射回类别名称
        top_label = class_names[top_idx[0].item()]

        # 返回类别名称和对应的概率值 (Python float类型)
        return top_label, top_prob[0].item()


def classify_image(image_path):
    """
    对外暴露的主函数，用于分类单个图像。
    它整合了模型加载、图像预处理和预测的全过程。

    :param image_path: 要识别的图片的本地文件路径
    :return: 一个元组 (category, probability)，例如 ('paper', 0.987)
    """
    # 如果模型未加载，则先执行加载
    if MODEL is None:
        _load_model_and_classes()

    try:
        # 1. 预处理图像
        input_tensor = _preprocess_image(image_path)

        # 2. 进行预测
        category, probability = _predict(MODEL, input_tensor, CLASS_NAMES)

        return category, probability
    except Exception as e:
        print(f"图像分类过程中出现错误: {e}")
        return None, None