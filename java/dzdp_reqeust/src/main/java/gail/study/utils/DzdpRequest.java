package gail.study.utils;

import cn.hutool.core.collection.CollectionUtil;
import cn.hutool.core.util.StrUtil;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import gail.study.entity.DpComment;
import net.dongliu.requests.Parameter;
import net.dongliu.requests.Requests;
import org.assertj.core.util.Lists;

import java.util.List;

import static gail.study.utils.DateUtils.parseDate;

public class DzdpRequest {


    public static List<DpComment> pollCommentPage(String shopId, String shopName, Integer pageNum) throws Exception {
        String resultStr = requestDzdp(shopId, pageNum);
        JSONObject resultJson = JSONObject.parseObject(resultStr);
        String msg = resultJson.getString("msg");
        if (StrUtil.isNotBlank(msg)) {
            throw new Exception(msg);
        }
        JSONArray list = resultJson.getJSONArray("list");
        if (CollectionUtil.isEmpty(list)) {
            return null;
        }
        List<DpComment> resultData = Lists.newArrayList();
        for (int i = 0; i < list.size(); i++) {
            JSONObject jsonObject = list.getJSONObject(i);
            resultData.add(DpComment.builder()
                    .shopId(shopId)
                    .shopName(shopName)
                    .content(jsonObject.getString("content"))
                    .star(jsonObject.getInteger("star"))
                    .price(jsonObject.getString("price"))
                    .userId(jsonObject.getJSONObject("feedUser").getLong("userId"))
                    .userName(jsonObject.getJSONObject("feedUser").getString("userName"))
                    .addTime(parseDate(jsonObject.getString("addTime")))
                    .build());
        }
        return resultData;

    }

    private static String requestDzdp(String shopId, Integer pageNum) {
        String resultStr = Requests.get("http://127.0.0.1/dpapi")
                .params(
                        Parameter.of("shop_id", shopId),
                        Parameter.of("start", pageNum * 25),
                        Parameter.of("sort", 1),
                        Parameter.of("data_type", 0),
                        Parameter.of("type", "comment"),
                        Parameter.of("token", "123123123")
                ).send().readToText();
        return resultStr;
    }


    public static void main(String[] args) throws Exception {
        List<DpComment> dzdpBster1 = pollCommentPage("H2bUha3iIucvNyht", "比斯特上海购物村精品奥特莱斯", 1);

        System.out.printf(dzdpBster1.toString());

    }


}
