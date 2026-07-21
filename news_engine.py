class NewsEngine:
    def calculate_news_impact(
        self,
        sentiment,
        confidence_level,
        impact_level,
        hours_old
    ):

        """
        新闻动态影响 V1.5
        """


        # 情绪方向

        if sentiment == "POSITIVE":

            direction = 1


        elif sentiment == "NEGATIVE":

            direction = -1


        else:

            direction = 0



        # 可信度权重

        confidence_weight = {

            "HIGH": 1.0,

            "MEDIUM": 0.5,

            "LOW": 0.2

        }.get(

            confidence_level,

            0.2

        )



        # 时间权重


        if hours_old <= 24:

            time_weight = 1.0


        elif hours_old <= 72:

            time_weight = 0.7


        elif hours_old <= 168:

            time_weight = 0.3


        else:

            time_weight = 0



        score = (

            direction

            *

            impact_level

            *

            confidence_weight

            *

            time_weight

        )



        return round(
            score,
            2
        )
    def evaluate_news_quality(
        self,
        source,
        relevance,
        hours_old
    ):

        """
        新闻可信度过滤 V1.4
        """


        score = 0


        # 来源评分

        if source == "official":

            score += 40


        elif source == "major_media":

            score += 30


        else:

            score += 10



        # 相关度

        score += relevance



        # 时间权重

        if hours_old <= 24:

            score += 20


        elif hours_old <= 72:

            score += 10


        else:

            score += 0



        if score > 100:

            score = 100



        if score >= 80:

            level = "HIGH"


        elif score >= 50:

            level = "MEDIUM"


        else:

            level = "LOW"



        return {

            "news_confidence":
            score,

            "level":
            level

        }
    def extract_keywords(
        self,
        market
    ):

        """
        市场关键词提取 V1.3.1
        """


        text = market.lower()


        # 删除无意义词

        remove_words = [

            "will",
            "win",
            "the",
            "before",
            "after",
            "yes",
            "no",
            "be",
            "a",
            "an",
            "of",
            "to"

        ]


        # 删除年份

        words = text.replace(
            "?",
            ""
        ).split()



        keywords = []


        for word in words:


            if word.isdigit():

                continue


            if word not in remove_words:

                keywords.append(
                    word
                )


        # 主题识别

        category = "OTHER"



        sports_words = [

            "world",
            "cup",
            "fifa",
            "football",
            "nba",
            "soccer"

        ]


        politics_words = [

            "president",
            "election",
            "vote",
            "government"

        ]


        crypto_words = [

            "bitcoin",
            "ethereum",
            "crypto",
            "btc"

        ]



        for word in keywords:


            if word in sports_words:

                category = "SPORTS"



            if word in politics_words:

                category = "POLITICS"



            if word in crypto_words:

                category = "CRYPTO"



        # 组合关键词

        if (
            "fifa" in keywords
            and
            "world" in keywords
            and
            "cup" in keywords
        ):

            keywords.remove(
                "world"
            )

            keywords.remove(
                "cup"
            )

            keywords.remove(
                "fifa"
            )


            keywords.append(
                "FIFA World Cup"
            )


        return {

            "keywords":
            keywords,


            "category":
            category

        }
    


    def analyze_news(
        self,
        market
    ):

        """
        新闻智能分析 V1.0

        输入:
        市场名称

        输出:
        新闻影响评分
        """


        keywords_positive = [
            "win",
            "victory",
            "support",
            "confirmed",
            "strong"
        ]


        keywords_negative = [
            "injury",
            "lose",
            "scandal",
            "ban",
            "problem"
        ]


        text = market.lower()


        positive = 0
        negative = 0


        for word in keywords_positive:

            if word in text:

                positive += 1



        for word in keywords_negative:

            if word in text:

                negative += 1



        if positive > negative:

            sentiment = "POSITIVE"

            impact_score = 70



        elif negative > positive:

            sentiment = "NEGATIVE"

            impact_score = 30



        else:

            sentiment = "NEUTRAL"

            impact_score = 50



        if sentiment == "POSITIVE":

            adjustment = 5


        elif sentiment == "NEGATIVE":

            adjustment = -5


        else:

            adjustment = 0



        return {

            "sentiment":
            sentiment,


            "impact_score":
            impact_score,


            "adjustment":
            adjustment,


            "risk_level":
            "MEDIUM"

        }