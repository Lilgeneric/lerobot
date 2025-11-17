# LeRobot 命令参考 (LeRobot Command Reference)

本文档提供了使用 `lerobot` 库进行机器人操作的常用命令，涵盖环境设置、硬件检查、数据采集、训练和推理。

## 1\. 环境设置与登录 (Setup & Login)

```bash
# 登录 Hugging Face (Login to Hugging Face)
huggingface-cli login --token ${HUGGINGFACE_TOKEN} --add-to-git-credential
HF_USER=$(huggingface-cli whoami | head -n 1)
echo $HF_USER

# (可选) 添加 Hugging Face 镜像源 (Optional: Add HF Mirror Endpoint)
export HF_ENDPOINT=https://hf-mirror.com

# 登录 Weights & Biases (Login to WandB)
wandb login ${wandb_API}
```

## 2\. 硬件检查 (Hardware Check)

```bash
# 检查视频端口 (Check video port)
ffplay /dev/video6

# 查找 LeRobot 兼容端口 (Find LeRobot compatible ports)
lerobot-find-port

# 查找 LeRobot 兼容相机 (Find LeRobot compatible cameras)
lerobot-find-cameras
```

## 3\. 校准 (Calibration)

```bash
# (如果需要) 赋予端口权限 (If needed, grant port permissions)
sudo chmod 666 /dev/ttyARM*

# 校准 Leader (Calibrate Leader)
lerobot-calibrate --teleop.type=so100_leader --teleop.port=/dev/ttyACM1 --teleop.id=my_leader

# 校准 Follower (Calibrate Follower)
lerobot-calibrate --robot.type=so100_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower
```

## 4\. 数据采集 (Data Collection)

```bash
# 运行数据采集 (Run data collection)
lerobot-record --robot.type=so100_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower --display_data=true \
--dataset.repo_id=aa/aa1 --dataset.num_episodes=25 --dataset.reset_time_s=10 --dataset.episode_time_s=120 \
--dataset.single_task="pick and place the object" --dataset.push_to_hub=false \
--robot.cameras='{
    camera1: {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
    camera2: {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30},
    camera3: {"type": "opencv", "index_or_path": 4, "width": 640, "height": 480, "fps": 30}
  }'\
--teleop.type=so100_leader --teleop.port=/dev/ttyACM1 --teleop.id=my_leader --play_sounds=false
```

## 5\. 数据查看 (Data Visualization)

```bash
lerobot-dataset-viz --repo-id aa22 --episode-index 0
```

## 6\. 模型训练 (Training)

### SmolVLA (带相机重命名)

注意：使用smolvla时，相机命名必须为`camera1/2/3`，如果不是注意`remap`。

```bash
lerobot-train --policy.path=lerobot/smolvla_base --dataset.repo_id=aa11 --batch_size=16 --steps=10000 \
--output_dir=outputs/train/my_smolvla12 --job_name=my_smolvla_training --policy.device=cuda \
--wandb.enable=false --policy.push_to_hub=false \
--rename_map='{"observation.images.top":"observation.images.camera1","observation.images.left":"observation.images.camera2","observation.images.right":"observation.images.camera3"}'
```

### SmolVLA (微调)

```bash
# smolbase 微调 (smolbase fine-tuning)
lerobot-train --policy.path=lerobot/smolvla_base --dataset.repo_id=aa_merged200 --batch_size=16 \
--steps=20000 --output_dir=outputs/train/my_smolvla14 --job_name=my_smolvla14_training \
--policy.device=cuda --wandb.enable=true --policy.push_to_hub=false
```

### SmolVLA (从头训练)

```bash
# smolbase 从头训练 (smolbase training from scratch)
lerobot-train --policy.type=smolvla --dataset.repo_id=aa_merged200 --batch_size=16 --steps=40000 \
--output_dir=outputs/train/my_smolvla14 --job_name=my_smolvla_training --policy.device=cuda \
--wandb.enable=false --policy.push_to_hub=false
```

### ACT (从头训练)

```bash
# act 从头训练 (act training from scratch)
lerobot-train --policy.type=act --dataset.repo_id=aa50 --batch_size=8 --steps=100000 \
--output_dir=outputs/train/my_act_single3 --job_name=my_act_single3_training \
--policy.device=cuda --wandb.enable=true --policy.push_to_hub=false
```

### Pi05 (微调)

```bash
# pi05 微调 (pi05 fine-tuning)
python src/lerobot/scripts/lerobot_train.py --dataset.repo_id=aa_merged280 --policy.type=pi05 \
--output_dir=./outputs/pi05_training2 --job_name=pi05_training2 \
--policy.pretrained_path=lerobot/pi05_base --policy.compile_model=true \
--policy.gradient_checkpointing=true --wandb.enable=true --policy.dtype=bfloat16 \
--steps=100000 --policy.device=cuda --batch_size=32 --policy.push_to_hub=false
```

## 7\. 模型推理 (Inference)

### 单臂推理 (Single-Arm Inference)

```bash
lerobot-record --robot.type=so100_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower --display_data=true \
--dataset.repo_id=aa/eval_97 --dataset.num_episodes=25 --dataset.reset_time_s=1 --dataset.episode_time_s=900 \
--dataset.single_task="" --dataset.push_to_hub=false \
--robot.cameras='{
    camera1: {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
    camera2: {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30},
    camera3: {"type": "opencv", "index_or_path": 4, "width": 640, "height": 480, "fps": 30}
  }'\
--policy.path=./outputs/train/my_act_single2/checkpoints/last/pretrained_model
```

### 双臂推理 (Bimanual Inference)

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