from pkg.Fdfd import Fdfd

if __name__ == '__main__':

    params = {
        "title": "CRM登录验证码",
        "content": "<div style=\"color:#666666;line-height:39px;\">【主营CRM】</div><div style=\"color:#666666;line-height:39px;\">您的账号：shanchaoyue</div><div style=\"color:#666666;line-height:39px;\">验证码是<span style=\"color:#5A9DF8\">373193</span>，请在10分钟内使用，若非本人操作，请立即反馈至IT部</div>",
        "user_ids": [
            "250213"
        ],
        "send_type": 1,
        "send_code": "373193",
        "user_name": "【主营CRM】shanchaoyue",
        "send_time": "2025-03-27 09:08:54",
        "failure_time": "2025-03-27 09:18:54",
        "timestamp": "1743066534",
        "sign": "7FB37D1FE1959C126A781BBE07976592",
        "action": "https://api.oa.fdttgroup.com/api/user/send-notice",
        "type": 2,
        "table_id": 0,
        "uuid": "5e9ebcc2-9ff1-c894-f60e-b5477cb16575"
    }

#     "INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('安徽经济管理干部学院', '专科', 90002001, 1);
# INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('湖南科技学院', '二本', 90002002, 1);
# INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('英国萨赛克斯大学', '一本', 90002003, 1);
# INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('北京交通大学', '211', 90002004, 1);
# INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('中国人民大学', '985', 90002005, 1);
# INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('哈尔滨工业大学', 'C9', 90002006, 1);
# INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('北京大学', '清北', 90002007, 1);
# INSERT INTO `fuda_oa`.`oa_university_level` (`university_name`, `level_name`, `level_id`, `status`) VALUES ('国家开放大学', '其他', 90002008, 1);"



    Fdfd(param=params, path="../.././data/requestLog.txt").testInterfaceSpeed()
