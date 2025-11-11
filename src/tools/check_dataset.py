import sys
from lerobot.datasets.lerobot_dataset import LeRobotDataset

if len(sys.argv) < 2:
    print("用法: python check_dataset.py <repo_id> [root]")
    sys.exit(1)

repo_id = sys.argv[1]
root = sys.argv[2] if len(sys.argv) > 2 else None

dataset = LeRobotDataset(repo_id, root=root)
print(f"Episodes: {dataset.meta.total_episodes}")