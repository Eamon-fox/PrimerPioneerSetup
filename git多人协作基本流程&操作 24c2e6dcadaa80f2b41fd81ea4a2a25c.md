# git多人协作基本流程&操作

---

- 初次使用
    - 下载安装git
    - 注册github账号
    - 配置github ssh key
    - 随便找个路径，git bash here
    - git config设置用户名、邮箱（最好和github账号一致）
    - git init初始化本地仓库
- 分头工作
    - git remote add origin <url>添加项目远程仓库
    - git pull origin master，把远程仓库主分支拉取到本地
    - git checkout -b <branch_name> master，在master上创建一个新分支
    - 进行某个功能的开发工作
    - git commit -m “完成了xxx”，把自己的工作在git中保存下来
    - git push origin <branch_name>，把代码推送到远程仓库的同名分支上
- 合并大家的工作
    - （如果这个分支的功能开发完了）先git pull origin master，和最新的远程仓库版本保持同步
        - 如果有冲突，手动处理一下（两处互相冲突的修改，保留哪一处）
    - 在github上提pull request，项目管理员决定要不要合到master中

可参考此链接便于理解：[https://blog.csdn.net/m0_60610428/article/details/148973022?spm=1001.2101.3001.6650.3&utm_medium=distribute.pc_relevant.none-task-blog-2~default~YuanLiJiHua~Position-3-148973022-blog-107328861.235^v43^control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2~default~YuanLiJiHua~Position-3-148973022-blog-107328861.235^v43^control&utm_relevant_index=6](https://blog.csdn.net/m0_60610428/article/details/148973022?spm=1001.2101.3001.6650.3&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EYuanLiJiHua%7EPosition-3-148973022-blog-107328861.235%5Ev43%5Econtrol&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EYuanLiJiHua%7EPosition-3-148973022-blog-107328861.235%5Ev43%5Econtrol&utm_relevant_index=6)

*但不要像博客里本地merge到dev分支然后直接push到远程dev分支，这样可能会覆盖掉别人的东西；最好只在自己的feature-xxx分支操作，合到dev时提pull request，由项目管理者整合