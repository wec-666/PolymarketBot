import logging
import os


# 创建日志文件夹

if not os.path.exists("logs"):
    os.makedirs("logs")



# =====================
# 机器人运行日志
# =====================

bot_logger = logging.getLogger("bot")

bot_logger.setLevel(logging.INFO)


bot_handler = logging.FileHandler(
    "logs/bot.log",
    encoding="utf-8"
)


formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)


bot_handler.setFormatter(formatter)


bot_logger.addHandler(bot_handler)



# =====================
# 交易日志
# =====================

trade_logger = logging.getLogger("trade")

trade_logger.setLevel(logging.INFO)


trade_handler = logging.FileHandler(
    "logs/trade.log",
    encoding="utf-8"
)


trade_handler.setFormatter(formatter)


trade_logger.addHandler(trade_handler)



# =====================
# 错误日志
# =====================

error_logger = logging.getLogger("error")

error_logger.setLevel(logging.ERROR)


error_handler = logging.FileHandler(
    "logs/error.log",
    encoding="utf-8"
)


error_handler.setFormatter(formatter)


error_logger.addHandler(error_handler)



# =====================
# 调用接口
# =====================

def log_info(message):

    bot_logger.info(message)



def log_trade(message):

    trade_logger.info(message)



def log_error(message):

    error_logger.error(message)