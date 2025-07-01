import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体支持
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("警告：中文字体设置失败，图表可能无法正确显示中文")


# 加载模型 - 使用与训练时完全相同的架构
def load_model(model_path, class_names):
    # 创建与训练时相同的模型架构
    model = models.resnet18(weights=None)  # 不加载预训练权重
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(class_names))

    # 加载模型状态
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()  # 设置为评估模式

    return model


# 图像预处理（与验证集相同）
def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)  # 添加批次维度


# 预测函数
def predict(model, input_tensor, class_names, topk=3):
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)

        # 获取topk预测结果
        top_probs, top_indices = torch.topk(probabilities, topk)
        top_probs = top_probs.numpy()
        top_indices = top_indices.numpy()

        # 获取对应的类别标签
        top_labels = [class_names[i] for i in top_indices]

        return list(zip(top_labels, top_probs))


# 可视化预测结果
def visualize_prediction(image_path, predictions):
    # 加载原始图像
    image = Image.open(image_path)

    # 创建图表
    plt.figure(figsize=(10, 8))

    # 显示图像
    plt.subplot(2, 1, 1)
    plt.imshow(image)
    plt.axis('off')
    plt.title('输入图像')

    # 显示预测结果
    plt.subplot(2, 1, 2)
    labels = [f"{label} ({prob:.2%})" for label, prob in predictions]
    probs = [prob for _, prob in predictions]

    # 水平条形图
    y_pos = np.arange(len(labels))
    plt.barh(y_pos, probs, align='center', color='skyblue')
    plt.yticks(y_pos, labels)
    plt.xlabel('置信度')
    plt.title('分类预测结果')
    plt.xlim(0, 1.0)

    # 添加数值标签
    for i, v in enumerate(probs):
        plt.text(v + 0.01, i, f"{v:.2%}", color='black', va='center')

    plt.tight_layout()
    plt.savefig('prediction_result.png')
    plt.show()


if __name__ == '__main__':
    # 模型和类别文件路径
    MODEL_PATH = 'garbage_classifier_resnet18.pth'
    CLASS_NAMES_FILE = 'class_names.txt'

    # 加载类别名称
    with open(CLASS_NAMES_FILE, 'r') as f:
        class_names = [line.strip() for line in f.readlines()]

    print(f"加载的类别: {class_names}")

    # 加载模型
    model = load_model(MODEL_PATH, class_names)
    print("模型加载完成")

    # 测试图像路径（替换为您自己的图像）
    test_images = [
        'C:/Users/刘又源/Desktop/1751353416114.jpg',
    ]

    # 创建测试图像目录（如果不存在）
    os.makedirs('test_images', exist_ok=True)
    print(f"请将测试图像放入 'test_images' 目录中")
    print(f"当前目录中的测试图像: {[f for f in os.listdir('test_images') if f.endswith(('.jpg', '.png'))]}")

    # 对每张测试图像进行预测
    for image_path in test_images:
        if not os.path.exists(image_path):
            print(f"\n测试图像不存在: {image_path}")
            continue

        print(f"\n处理图像: {image_path}")

        # 预处理图像
        input_tensor = preprocess_image(image_path)

        # 进行预测
        predictions = predict(model, input_tensor, class_names, topk=1)

        # 显示预测结果
        print("预测结果 :")
        for label, prob in predictions:
            print(f"  {label}: {prob:.2%}")

        # 可视化结果
        visualize_prediction(image_path, predictions)
        print("预测结果已保存为 'prediction_result.png'")


def classify_image():
    return None