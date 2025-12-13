HIL-SERL 的工作流。

### 第一阶段：环境准备与安装

**1. 安装带 HIL-SERL 组件的 LeRobot**
首先确保你安装了包含 `hilserl` 额外依赖的 LeRobot 环境。

  * **指令：**
    ```bash
    pip install -e ".[hilserl]"
    ```
  * [cite_start]**功能：** 安装 HIL-SERL 算法运行所需的所有核心库和依赖项 [cite: 20, 21]。

-----

### 第二阶段：硬件配置与限制

**2. 确定从臂（Follower）的工作空间边界**
在开始之前，你需要确定机械臂末端执行器（End-Effector）的安全移动范围，防止其在训练中乱动。你需要使用主臂（Leader）控制从臂移动来测定这些边界。

  * **指令：**
    ```bash
    lerobot-find-joint-limits \
      --robot.type=so100_follower \
      --robot.port=/dev/ttyACM1 \
      --robot.id=my_follower \
      --teleop.type=so100_leader \
      --teleop.port=/dev/ttyACM0 \
      --teleop.id=my_leader \
      --urdf_path=/home/generic/lerobot/Simulation/SO101/so101_new_calib.urdf \
      --target_frame_name=gripper_frame_link \
      --teleop_time_s=120
    ```
    *(注意：请根据你的实际端口号和机器人ID修改参数)*
  * [cite_start]**功能：** 运行脚本后，移动主臂带动从臂遍历任务空间。脚本会输出末端执行器的最大/最小位置（Max/Min ee position）[cite: 56, 59]。
  * [cite_start]**后续操作：** 将输出的数值填入你的环境配置文件（`env_config.json`）中的 `end_effector_bounds` 字段 [cite: 60]。

-----

### 第三阶段：数据收集与处理

**3. 配置主臂遥操作并收集示教数据**
[cite_start]你需要录制少量的离线示教数据来启动训练。因为你有主臂，需要在配置文件中将 `teleop` 类型设为 Leader Arm（如 `so101_leader`）而不是手柄 [cite: 78]。

  * [cite_start]**配置修改建议：** 确保配置文件中 `env.teleop.type` 设置为你的主臂型号，且 `mode` 设置为 `"record"` [cite: 62, 78]。
  * **指令：**
    ```bash
    python -m lerobot.rl.gym_manipulator --config_path src/lerobot/json/env_config_keyboard.json
    ```
  * [cite_start]**功能：** 启动录制模式。你需要操作主臂完成任务，并在成功时按键盘 `s` 键，失败按 `esc` 键（或配置文件指定的按键）[cite: 79, 81]。这将生成用于预训练的数据集。

**4. 图像裁剪（处理所有摄像头）**
为了减少背景干扰，需要对你那 **3 个摄像头**的画面进行裁剪，只保留任务区域。

  * **指令：**
    ```bash
    python -m lerobot.rl.crop_dataset_roi --repo-id your_username/your_dataset_name
    ```
  * [cite_start]**功能：** 启动交互式工具。你需要为每个摄像头视角框选感兴趣区域（ROI）。脚本会生成裁剪参数，你需要将这些参数更新到训练配置文件的 `image_preprocessing` 部分 [cite: 87, 88]。

-----

### 第四阶段：训练奖励分类器（强烈推荐）

**5. 训练奖励分类器 (Reward Classifier)**
HIL-SERL 依赖视觉模型来自动判断任务是否成功，从而给出奖励信号。虽然你可以手动给出奖励，但为了自动化训练，建议训练一个分类器。

  * **指令：**
    ```bash
    lerobot-train --config_path src/lerobot/json/reward_classifier_train_config.json
    ```
  * [cite_start]**功能：** 使用刚才收集的示教数据（包含成功和失败的案例）训练一个视觉分类器 [cite: 111]。
  * [cite_start]**后续操作：** 训练完成后，将模型路径更新到 HIL-SERL 的环境配置文件中 (`reward_classifier.pretrained_path`) [cite: 112]。

  * [cite_start]**测试train完的reward_classifier** 
  * **指令：**
    ```bash
    python -m lerobot.rl.gym_manipulator --config_path src/lerobot/json/env_config_keyboard_rc.json
    ```

-----

### 第五阶段：启动 HIL-SERL 训练（Actor-Learner 架构）

HIL-SERL 使用分布式架构，需要同时开启两个终端窗口，分别运行 **Learner（学习者）** 和 **Actor（执行者）**。

**6. 启动 Learner (终端 1)**

  * **指令：**
    ```bash
    python -m lerobot.rl.learner --config_path src/lerobot/json/rl_train_config.json
    ```
  * [cite_start]**功能：** 初始化策略网络，处理数据并更新策略权重。它会开启一个服务器等待 Actor 连接 [cite: 125]。
  * [observation.state]**修改：** shape为18维，就是6维的关节角度还有上面所讲的其它附加信息。请用上面采集数据集目录下的meta/stats.json中的统计信息填充此配置文件。

**7. 启动 Actor (终端 2)**

  * **指令：**
    ```bash
    python -m lerobot.rl.actor --config_path src/lerobot/json/rl_train_config.json
    ```
  * [cite_start]**功能：** 连接到 Learner，在真实机器人上执行策略。它会收集经验数据发送给 Learner，并定期拉取最新的策略权重 [cite: 125, 126]。

-----

### 实验中的关键操作（Human-in-the-Loop）

在 Actor 运行过程中，你需要通过介入来引导机器人：

  * [cite_start]**介入操作：** 当机器人动作偏离或危险时，按下主臂对应的介入键（通常配置为键盘 `space` 或手柄按键）夺取控制权 [cite: 127]。
  * [cite_start]**操作逻辑：** 按一下暂停策略并由你接管 -\> 纠正机器人动作 -\> 再按一下交还控制权给策略 [cite: 80, 128]。

**总结执行顺序：**

1.  `pip install` (安装)
2.  `lerobot-find-joint-limits` (定边界)
3.  `gym_manipulator` (录数据)
4.  `crop_dataset_roi` (裁图像)
5.  `lerobot-train` (训奖励模型)
6.  `learner` + `actor` (双终端启动训练)