package gail.study.utils;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.Locale;

/**
 * @author Gail_Hu
 * @version 1.0
 * @title DateUtils
 * @description 日期工具类
 * @create 2024/05/08 16:19
 */
public class DateUtils {
    /**
     * 将字符串日期 MMM d, yyyy h:mm:ss a 转成 LocalDateTime
     * @param dateStr 字符串日期
     * @return LocalDateTime日期
     */
    public static LocalDateTime parseDate(String dateStr) {
        SimpleDateFormat formatter = new SimpleDateFormat("MMM d, yyyy h:mm:ss a", Locale.ENGLISH);
        try {
            Date date = formatter.parse(dateStr);
            return LocalDateTime.ofInstant(date.toInstant(), ZoneId.systemDefault());
        } catch (ParseException e) {
            e.printStackTrace();
            throw new RuntimeException("dateTime parse error!");
        }
    }
}
