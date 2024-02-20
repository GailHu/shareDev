package com.gail.dev.common.config;

import org.springframework.context.annotation.Bean;
import org.springframework.scheduling.TaskScheduler;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;

/**
 * @author Gail_Hu
 * @version 1.0
 * @title SchedulerConfig
 * @description
 * @create 24.2.19 13:27
 */
public class SchedulerConfig {
    @Bean
    public TaskScheduler taskScheduler() {
        return new ThreadPoolTaskScheduler();
    }
}
