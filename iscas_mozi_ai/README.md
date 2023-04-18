# iscas_mozi_ai

`iscas_mozi_ai` 是在墨子个人版仿真平台上，基于行为树的知识规则智能体开发仓库.

## 智能体开发

- **存放位置：** 个人开发的智能体以独立文件夹的形式组织，互不干扰。如`red_agent_lk_v1`为李凯开发的红方知识规则智能体，目录里面`util`文件夹包含行为树结构以及执行动作。`main_versus.py`可以与内置AI对抗，供`iscas_mozi_ai/test.py`调用以测试对抗内置AI的水平.

- **配置文件：**`env`文件夹包含`env.py`和`etc.py`。`env.py`不需要更改，`etc.py`和运行墨子环境配置有关，包括想定、运行模式等.


## 对抗模式

对抗模式包含与**内置AI**对抗和与**其他开发人员**构建的知识规则智能体对抗.

- 与内置AI对抗：运行`test.py`,可参考如下示例。

    ```
    import logging
    logging.basicConfig(format="【%(asctime)s】-【%(levelname)s】: %(message)s",
                    datefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.DEBUG)

    from red_agent_lk_v1 import main_versus
    ```

- 机机对抗：运行main.py，如下示例表示红方的lk和蓝方的hk对抗,总体调度逻辑不需要修改.
    ```
    from blue_agent_hk_v1.utils.bt_agent_antiship import CAgent as Blue_agent
    # from blue_agent_lj_v1.utils.bt_agent_antiship import CAgent as Blue_agent
    # from red_agent_zzh_v1.utils.bt_red_defence import ZZHAgent as Red_agent
    from red_agent_lk_v1.utils.bt_agent_join_defence import CAgent as Red_agent
    ```
## 其他

- 个人构建自己的分支，不能在`master`分支上开发
- 建议采用`logging`日志器，减少使用`print`
- 有任何疑问请及时联系李凯

