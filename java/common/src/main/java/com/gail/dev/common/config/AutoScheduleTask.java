package com.gail.dev.common.config;


import cn.hutool.core.io.FileUtil;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONUtil;
import com.gail.dev.common.entity.TaskEntity;
import com.gail.dev.common.service.DownloadFileTask;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.scheduling.TaskScheduler;
import org.springframework.scheduling.support.CronTrigger;

import javax.annotation.Resource;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;

/**
 * @author Gail_Hu
 * @version 1.0
 * @title AutoScheduleTaskConfig
 * @description 自动运行定时任务配置
 * @create 24.2.5 11:39
 */
//@Component
@Slf4j
public class AutoScheduleTask implements ApplicationListener<ContextRefreshedEvent> {

    @Value("${sys.taskConfigPath}")
    private String configPath;

    @Resource
    private TaskScheduler taskScheduler;
    @Override
    public void onApplicationEvent(ContextRefreshedEvent contextRefreshedEvent) {
        initTask();
    }
    private void initTask() {
        if (FileUtil.exist(configPath)){
            StringBuilder content = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new FileReader(configPath))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    content.append(line);
                }

            } catch (IOException e) {
                throw new RuntimeException(e);
            }
            String fileContent = content.toString();
            if (!fileContent.isEmpty()){
                List<TaskEntity> taskList = JSONUtil.toList(new JSONArray(fileContent), TaskEntity.class);
                for (TaskEntity task: taskList) {
                    taskScheduler.schedule(new DownloadFileTask(task), new CronTrigger(task.getCorn()));
                }
                log.info("初始成功，共{}个定时任务！", taskList.size());
                return;
            }
            log.warn("配置文件为空，加载定时任务退出！");
            return;
        }
        log.warn("{}配置文件不存在，定时任务未初始化！", configPath);
    }

}
