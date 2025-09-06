#/bin/bash

pip uninstall -y mock-voice

# 手动删除残留文件（若存在）
rm -rf /home/yang/miniconda3/envs/test_eval_frame/lib/python3.10/site-packages/mock_voice*
rm -f /home/yang/miniconda3/envs/test_eval_frame/bin/mock-voice

pip uninstall -y ops-mem

# 手动删除残留文件（若存在）
rm -rf /home/yang/miniconda3/envs/test_eval_frame/lib/python3.10/site-packages/ops-mem*
rm -f /home/yang/miniconda3/envs/test_eval_frame/bin/ope-mem


pip uninstall -y ops-scheduler --no-cache-dir

pip uninstall -y ops-llm-agent --no-cache-dir

pip uninstall -y ops-weather --no-cache-dir

pip uninstall -y ops-miband --no-cache-dir

pip cache purge
