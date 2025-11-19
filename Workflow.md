# 🤖 LeRobot 操作指南 (LeRobot Command Reference)

本文档提供了使用 `lerobot` 库进行机器人操作的完整工作流命令，涵盖环境配置、硬件调试、数据全生命周期管理（采集、处理、查看）、模型训练及推理评估。

-----

## 📋 目录 (Table of Contents)

1.  [环境设置与登录](https://www.google.com/search?q=%231-%E7%8E%AF%E5%A2%83%E8%AE%BE%E7%BD%AE%E4%B8%8E%E7%99%BB%E5%BD%95-setup--login)
2.  [硬件检查与校准](https://www.google.com/search?q=%232-%E7%A1%AC%E4%BB%B6%E6%A3%80%E6%9F%A5%E4%B8%8E%E6%A0%A1%E5%87%86-hardware--calibration)
3.  [数据采集](https://www.google.com/search?q=%233-%E6%95%B0%E6%8D%AE%E9%87%87%E9%9B%86-data-collection)
4.  [数据管理与操作](https://www.google.com/search?q=%234-%E6%95%B0%E6%8D%AE%E7%AE%A1%E7%90%86%E4%B8%8E%E6%93%8D%E4%BD%9C-data-operations)
5.  [数据集详情](https://www.google.com/search?q=%235-%E6%95%B0%E6%8D%AE%E9%9B%86%E8%AF%A6%E6%83%85-dataset-specifications)
6.  [模型训练](https://www.google.com/search?q=%236-%E6%A8%A1%E5%9E%8B%E8%AE%AD%E7%BB%83-training)
7.  [模型推理](https://www.google.com/search?q=%237-%E6%A8%A1%E5%9E%8B%E6%8E%A8%E7%90%86-inference)
8.  [模型性能记录](https://www.google.com/search?q=%238-%E6%A8%A1%E5%9E%8B%E6%80%A7%E8%83%BD%E8%AE%B0%E5%BD%95-model-performance)

-----

## 1\. 环境设置与登录 (Setup & Login)

在开始之前，请确保已配置好 Hugging Face 和 W\&B 的认证信息。

```bash
# 1. 登录 Hugging Face (Login to Hugging Face)
huggingface-cli login --token ${HUGGINGFACE_TOKEN} --add-to-git-credential

# 验证登录用户
HF_USER=$(huggingface-cli whoami | head -n 1)
echo "Current HF User: $HF_USER"

# (可选) 如果在国内，添加 Hugging Face 镜像源
export HF_ENDPOINT=https://hf-mirror.com

# 2. 登录 Weights & Biases (Login to WandB)
wandb login ${wandb_API}
```

-----

## 2\. 硬件检查与校准 (Hardware & Calibration)

### 硬件自检 (Hardware Check)

```bash
# 检查视频流 (Check video port)
ffplay /dev/video6

# 自动查找 LeRobot 兼容的串行端口
lerobot-find-port

# 自动查找 LeRobot 兼容的相机
lerobot-find-cameras
```

### 机械臂校准 (Calibration)

> **注意**: 首次连接或更换端口后，可能需要赋予 USB 端口权限。

```bash
# 赋予端口读写权限
sudo chmod 666 /dev/ttyARM*

# 校准主手 (Leader Arm)
lerobot-calibrate --teleop.type=so100_leader --teleop.port=/dev/ttyACM1 --teleop.id=my_leader

# 校准从手 (Follower Arm)
lerobot-calibrate --robot.type=so100_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower
```

-----

## 3\. 数据采集 (Data Collection)

使用以下命令录制遥操作数据。请根据实际相机 ID 修改 `index_or_path`。

```bash
lerobot-record \
  --robot.type=so100_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_follower \
  --display_data=true \
  --dataset.repo_id=aa/aa1 \
  --dataset.num_episodes=25 \
  --dataset.reset_time_s=10 \
  --dataset.episode_time_s=120 \
  --dataset.single_task="pick and place the object" \
  --dataset.push_to_hub=false \
  --robot.cameras='{
    camera1: {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
    camera2: {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30},
    camera3: {"type": "opencv", "index_or_path": 4, "width": 640, "height": 480, "fps": 30}
  }' \
  --teleop.type=so100_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=my_leader \
  --play_sounds=false
```

-----

## 4\. 数据管理与操作 (Data Operations)

### 可视化与统计

```bash
# 数据集可视化 (查看第0条episode)
lerobot-dataset-viz --repo-id aa22 --episode-index 0

# 查看数据集条数 (使用自定义脚本)
python src/tools/check_dataset.py aa50
```

### 数据集合并 (Dataset Merging)

将训练集和验证集合并为一个新的数据集：

```bash
python -m lerobot.scripts.lerobot_edit_dataset \
  --repo_id lerobot/pusht_merged \
  --operation.type merge \
  --operation.repo_ids "['lerobot/pusht_train', 'lerobot/pusht_val']"
```

-----

## 5\. 数据集详情 (Dataset Specifications)

以下是当前可用数据集的详细说明及统计。

### 📷 相机视角示意

> **aa22, aa50, aa\_merged200, aa\_merged280** 数据集均采用以下相机布局：
>

### 📊 数据集列表

| 数据集 ID | 数据条数 | 物品数量 | 任务描述与细节 |
| :--- | :---: | :---: | :--- |
| **aa11** | 25 | 6 | **单物品随机抓取**。<br>共有6种药品，每条数据随机抓取其中1个。 |
| **aa16** | 13 | 4 | **单物品随机抓取**。<br>共有4种药品，每条数据随机抓取其中1个。 |
| **aa22** | 30 | 2 | **固定顺序多物品抓取**。<br>共有2个药盒。每条数据按序依次取放：先连花清瘟，后复方。 |
| **aa50** | 80 | 4 | **单一场景大量重复**。<br>共有4种药品。每次盒子中仅有1个药品，每种药品重复抓取20次。 |
| **aa\_merged200** | 200 | 4 | **复杂场景连续抓取**。<br>盒子中同时存在4种药品。任务为依次抓取直至清空，4次抓取为一组，共约33组。<br>**优先级顺序**：连花清瘟 \> 复方 \> 驱叮液 \> 安神胶囊。 |
| **aa\_merged280** | 280 | 4 | **混合数据集**。<br>包含 `aa50` (80条) + `aa_merged200` (200条)。 |

#### 以下附aa22、aa50、aa_merged200、aa_merged280数据集相机视角
![alt text](<docs/doc/Camera_perspective.png>)

-----

## 6\. 模型训练 (Training)

### 🧠 SmolVLA 模型

> **⚠️ 关键提示**: 使用 SmolVLA 时，相机命名必须为 `camera1`, `camera2`, `camera3`。如果数据集中命名不一致，务必使用 `--rename_map` 参数。

**1. 带相机重命名的训练 (With Camera Remap)**

```bash
lerobot-train --policy.path=lerobot/smolvla_base --dataset.repo_id=aa11 --batch_size=16 --steps=10000 \
--output_dir=outputs/train/my_smolvla12 --job_name=my_smolvla_training --policy.device=cuda \
--wandb.enable=false --policy.push_to_hub=false \
--rename_map='{"observation.images.top":"observation.images.camera1","observation.images.left":"observation.images.camera2","observation.images.right":"observation.images.camera3"}'
```

**2. 微调 (Fine-tuning)**

```bash
lerobot-train --policy.path=lerobot/smolvla_base --dataset.repo_id=aa_merged200 --batch_size=16 \
--steps=20000 --output_dir=outputs/train/my_smolvla14 --job_name=my_smolvla14_training \
--policy.device=cuda --wandb.enable=true --policy.push_to_hub=false
```

**3. 从头训练 (Training from Scratch)**

```bash
lerobot-train --policy.type=smolvla --dataset.repo_id=aa_merged200 --batch_size=16 --steps=40000 \
--output_dir=outputs/train/my_smolvla14 --job_name=my_smolvla_training --policy.device=cuda \
--wandb.enable=false --policy.push_to_hub=false
```

### 🦾 ACT 模型

**从头训练 (Training from Scratch)**

```bash
lerobot-train --policy.type=act --dataset.repo_id=aa50 --batch_size=8 --steps=100000 \
--output_dir=outputs/train/my_act_single3 --job_name=my_act_single3_training \
--policy.device=cuda --wandb.enable=true --policy.push_to_hub=false
```

### 🥧 Pi05 模型

**微调 (Fine-tuning)**

```bash
python src/lerobot/scripts/lerobot_train.py --dataset.repo_id=aa_merged280 --policy.type=pi05 \
--output_dir=./outputs/pi05_training2 --job_name=pi05_training2 \
--policy.pretrained_path=lerobot/pi05_base --policy.compile_model=true \
--policy.gradient_checkpointing=true --wandb.enable=true --policy.dtype=bfloat16 \
--steps=100000 --policy.device=cuda --batch_size=32 --policy.push_to_hub=false
```

-----

## 7\. 模型推理 (Inference)

### 单臂推理 (Single-Arm)

```bash
lerobot-record --robot.type=so100_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower \
--display_data=true --dataset.repo_id=aa/eval_97 --dataset.num_episodes=25 \
--dataset.reset_time_s=1 --dataset.episode_time_s=900 --dataset.single_task="" \
--dataset.push_to_hub=false \
--robot.cameras='{
    camera1: {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
    camera2: {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30},
    camera3: {"type": "opencv", "index_or_path": 4, "width": 640, "height": 480, "fps": 30}
  }'\
--policy.path=./outputs/train/my_act_single2/checkpoints/last/pretrained_model
```

### 双臂推理 (Bimanual)

```bash
lerobot-record --robot.type=bi_so100_follower --robot.left_arm_port=/dev/ttyACM1 --robot.right_arm_port=/dev/ttyACM0 \
--robot.id=bimanual_follower --display_data=true --dataset.repo_id=aa/eval_1 --dataset.num_episodes=25 \
--dataset.single_task="" --dataset.push_to_hub=false \
--robot.cameras='{
    camera1: {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
    camera2: {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30},
    camera3: {"type": "opencv", "index_or_path": 4, "width": 640, "height": 480, "fps": 30}
  }'\
--policy.path=./outputs/train/my_smolvla/checkpoints/001000/pretrained_model
```

-----

## 8\. 模型性能记录 (Model Performance)

以下记录了不同模型检查点在特定任务上的表现：

| 模型架构 | 检查点路径 (Checkpoint Path) | 任务场景 | 成功率 | 备注 |
| :--- | :--- | :--- | :---: | :--- |
| **Pi05** | `.../pi05_training/checkpoints/080000` | 3个药品依次抓取 | **\~80%** | 具有明确的抓取顺序 |
| **ACT** | `.../my_act_single2/checkpoints/100000` | 3个药盒中随机单个 | **\~90%** | 针对任意单个药品的抓取能力强 |