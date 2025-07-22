package com.gail.dev.common.service;

import cn.hutool.json.JSONUtil;
import com.gail.dev.common.entity.TaskEntity;
import lombok.extern.slf4j.Slf4j;


/**
 * @author Gail_Hu
 * @version 1.0
 * @title DownloadFileTask
 * @description
 * @create 24.2.19 12:05
 */
@Slf4j
public class DownloadFileTask implements Runnable{
    private TaskEntity taskEntity;

    public DownloadFileTask(TaskEntity taskEntity) {
        this.taskEntity = taskEntity;
    }
    @Override
    public void run() {
        String taskName = taskEntity.getTaskName();
        String srcPath = taskEntity.getSrcPath();
        String targetPath = taskEntity.getTargetPath();
        // 文件命名规则引擎
        log.info("Executing task with parameter: " + JSONUtil.toJsonStr(taskEntity));
    }
}
