package com.gail.dev.common.entity;

import lombok.Data;

/**
 * @author Gail_Hu
 * @version 1.0
 * @title TaskEntity
 * @description
 * @create 24.2.19 12:04
 */
@Data
public class TaskEntity {
    private String taskName;
    private String srcPath;
    private String targetPath;
    private String corn;
    private String description;
}
