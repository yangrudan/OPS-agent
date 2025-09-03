# 构建过程的常见错误和处理方式

## build报错: 

```bash
ops-mem-agent: stdout   Successfully installed ops-mem-0.0.1


[ERROR]
failed to build node `ops-mem-agent`

Caused by:
   0: build command failed
   1: build command `pip install -e ../../agent-hub/ops-mem` returned exit status: 1

Location:
    libraries/core/src/build/build_command.rs:79:24
```

处理方式

```bash
pip uninstall -y mock-voice

# 手动删除残留文件（若存在）
rm -rf /home/yang/miniconda3/envs/test_eval_frame/lib/python3.10/site-packages/mock_voice*
rm -f /home/yang/miniconda3/envs/test_eval_frame/bin/mock-voice

pip uninstall -y ops-mem

# 手动删除残留文件（若存在）
rm -rf /home/yang/miniconda3/envs/test_eval_frame/lib/python3.10/site-packages/ops-mem*
rm -f /home/yang/miniconda3/envs/test_eval_frame/bin/ope-mem
```
