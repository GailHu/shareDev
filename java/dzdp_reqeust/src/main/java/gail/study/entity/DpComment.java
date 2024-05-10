package gail.study.entity;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * @author Gail_Hu
 * @version 1.0
 * @title DpComment
 * @description 大众点评
 * @create 2024/05/08 15:36
 */
@Data
@Builder
public class DpComment {
    private String shopId;
    private String shopName;
    private String content;
    private Integer star;
    private String price;
    private Long userId;
    private String userName;
    private LocalDateTime addTime;
}
