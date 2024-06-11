CREATE DATABASE IF NOT EXISTS `ai_video`;

USE ai_video;

CREATE TABLE IF NOT EXISTS ai_user(
  `uid` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `phone` VARCHAR(11) NOT NULL COMMENT '手机号',
  `password` VARCHAR(255) NOT NULL COMMENT '密码',
  `email` VARCHAR(100) default NULL COMMENT '邮箱',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `login_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上次登录时间',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `phonel_UNIQUE` (`phone`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS ai_user_tokens(
  `uid` INT NOT NULL COMMENT '用户ID',
  `token` VARCHAR(255) NOT NULL COMMENT '登录token',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY(`uid`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS ai_task_video_gen(
  `vid_id` INT NOT NULL AUTO_INCREMENT COMMENT '视频生成任务ID',
  `uid` INT NOT NULL COMMENT '用户ID',
  `subject` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '视频主题，用于AI生成文案',
  `resolution` VARCHAR(10) NOT NULL COMMENT '分辨率',
  `style` VARCHAR(100) NOT NULL COMMENT '图片风格',
  `script` TEXT NOT NULL COMMENT '视频文案，用户未输入时使用AI生成',
  `paragraph` INT NOT NULL COMMENT '视频文案段落数，一段生成一张图片',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '任务创建时间',
  `finished_at` TIMESTAMP DEFAULT NULL COMMENT '任务完成时间',
  `percent` INT DEFAULT 0 COMMENT '任务完成百分比',
  `status` INT DEFAULT 0 COMMENT '任务状态。 0： 待完成 1：成功 2：失败',
  `reason` VARCHAR(255) DEFAULT NULL COMMENT '任务失败时记录原因',
  PRIMARY KEY(`vid_id`),
  FOREIGN KEY(`uid`) REFERENCES `ai_user`(`uid`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS ai_task_img_gen(
  `img_id` INT NOT NULL AUTO_INCREMENT COMMENT '图片生成任务ID',
  `vid_id` INT NOT NULL COMMENT '对应的视频任务ID',
  `text_content` VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '生成图片的文案',
  `resolution` VARCHAR(10) NOT NULL COMMENT '生成图片的分辨率',
  `style` VARCHAR(100) DEFAULT NULL COMMENT '图片风格',
  `num` INT DEFAULT 1 COMMENT '生成图片数量',
  `log_id` INT DEFAULT 0 COMMENT '图片生成接口返回的请求唯一标识码',
  `taskId` INT DEFAULT 0 COMMENT '图片生成接口返回的任务 ID',
  `data` JSON DEFAULT NULL COMMENT '图片生成任务查询接口返回的生成结果',
  `finished_at` TIMESTAMP DEFAULT NULL COMMENT '任务结束时间',
  `status` INT DEFAULT 0 COMMENT '任务状态 0：待完成 1：成功 其他：失败（接口错误码）',
  `reason` VARCHAR(255) DEFAULT NULL COMMENT '任务失败时记录原因',
  PRIMARY KEY(`img_id`),
  FOREIGN KEY(`vid_id`) REFERENCES `ai_task_video_gen`(`vid_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;