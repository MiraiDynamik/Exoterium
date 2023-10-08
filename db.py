import sqlite3
import time
from algoliasearch.recommend_client import RecommendClient

recommendClient = RecommendClient.create("SF0IKHXEOM", "fad1aa330a1a4c92f332df2159732ea3")


def InitDB():
    conn = sqlite3.connect('./history.db')
    conn.execute(
        "CREATE TABLE IF NOT EXISTS algolia_data (id INTEGER PRIMARY KEY, user_id VARCHAR, paper_id VARCHAR, recommend_id VARCHAR,  recommend_title VARCHAR, type INTEGER, create_time timestamp)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS read_history (id INTEGER PRIMARY KEY, user_id VARCHAR, paper_id VARCHAR, type INTEGER)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recommendations (id INTEGER PRIMARY KEY, user_id VARCHAR, recommend_id VARCHAR, recommend_title VARCHAR)"
    )
    conn.close()


def SaveRecordReadingHistory(type, userID, paperID):
    if type == 1:
        print("Reading_Paper_Record_Abstract", userID, paperID)
    elif type == 2:
        print("Reading_Paper_Record_Detail", userID, paperID)

    result = GetRecommendPaper(paperID)
    SaveRecommendRecord(userID, paperID, result, 2)
    UpdateRecommendWithWeight(userID)


# Get recommendPaper's object_id
def GetRecommendPaper(object_id):
    result = []
    # Get Recommend Paper
    recommendData = recommendClient.get_related_products(
        [
            {
                "indexName": "test_arXiv",
                "objectID": object_id,
            },
        ]
    )

    recommendData = recommendData['results'][0]['hits']
    result = []
    for x in recommendData:
        tmp = (x['objectID'], x['title'])
        result.append(tmp)
    return result


def SaveRecommendRecord(userID, paperID, result, type):
    conn = sqlite3.connect('./history.db')
    cursor = conn.cursor()

    # Save read record
    cursor.execute('INSERT INTO read_history (user_id, paper_id, type) VALUES (?, '
                   '?, ?)', (userID, paperID, type))

    # 检查当前user_id的algolia_data中是否已经存在paper_id，防止重复保存。
    cursor.execute("""
           SELECT 1
           FROM algolia_data
           WHERE user_id = ? AND paper_id = ?
           LIMIT 1
       """, (userID, paperID))
    exists = cursor.fetchone()

    if not exists:
        # Save algolia_data
        result = GetRecommendPaper(paperID)
        t = time.time()
        for object_id, recommend_title in result:
            cursor.execute(
                'INSERT INTO algolia_data (user_id, paper_id, recommend_id, recommend_title, type, create_time) VALUES ('
                '?, ?, ?, ?, ?, ?)', (userID, paperID, object_id, recommend_title, type, t))

        # Keep nearly 5 recommendation records for each user
        cursor.executescript("""
                        WITH Ranked AS (
                            SELECT 
                                id,
                                user_id,
                                ROW_NUMBER() OVER (
                                    PARTITION BY user_id 
                                    ORDER BY create_time DESC, id DESC
                                ) AS rn
                            FROM 
                                algolia_data
                        )
                        DELETE FROM algolia_data
                        WHERE id IN (
                            SELECT id
                            FROM Ranked
                            WHERE rn > 150
                        );
                    """)

    conn.commit()
    conn.close()


# Update recommendations
def UpdateRecommendWithWeight(userID):
    # 根据如下规则推荐：
    # 1.文章被推荐次数
    # 2.用户是否已阅读
    # 3.用户阅读的是文章内容还是摘要

    # connect database
    conn = sqlite3.connect('./history.db')
    cursor = conn.cursor()

    # 获取用户每篇文章的被推荐次数、推荐类型(由于阅读还是摘要导致的推荐)和推荐标题
    cursor.execute("""
        SELECT recommend_id, recommend_title, COUNT(*) as recommend_count, MAX(type) as max_type
        FROM algolia_data
        WHERE user_id = ?
        GROUP BY recommend_id, recommend_title
    """, (userID,))
    recommend_data = cursor.fetchall()

    # 获取用户阅读记录
    cursor.execute("""
        SELECT paper_id, type
        FROM read_history
        WHERE user_id = ?
    """, (userID,))
    user_reads = cursor.fetchall()

    # 将用户的阅读记录转换为方便查询的字典
    user_read_dict = {paper_id: type for paper_id, type in user_reads}

    # 计算每篇推荐文章的权重
    weights = {}
    for recommend_id, recommend_title, recommend_count, max_type in recommend_data:
        weight = recommend_count  # 初始权重为推荐次数
        if recommend_id in user_read_dict:
            weight -= 50  # 如果用户已读过该推荐文章，权重减少50
        if max_type == 2:
            weight += 10  # 如果推荐是基于用户阅读文章的全文产生的，权重增加10

        weights[(recommend_id, recommend_title)] = weight

    # 根据权重排序推荐文章，并选择权重最高的n篇文章
    n = 10
    top_recommendations = [(recommend_id, recommend_title) for (recommend_id, recommend_title), weight in
                           sorted(weights.items(), key=lambda x: x[1], reverse=True)[:n]]

    # 推荐结果存储到数据库中
    recommend_records = [(userID, recommend_id, recommend_title) for recommend_id, recommend_title in
                         top_recommendations]

    # 删除该用户之前的推荐结果
    cursor.execute("""
        DELETE FROM recommendations
        WHERE user_id = ?
    """, (userID,))

    # 插入推荐数据到数据库
    cursor.executemany("""
        INSERT INTO recommendations (user_id, recommend_id, recommend_title)
        VALUES (?, ?, ?)
    """, recommend_records)

    conn.commit()
    conn.close()


def GetRecommendData(userID):
    conn = sqlite3.connect('./history.db')  # 请确保此路径指向你的数据库
    cursor = conn.cursor()

    cursor.execute('SELECT recommend_id, recommend_title FROM recommendations WHERE user_id = ?', (userID,))
    rows = cursor.fetchall()

    conn.close()

    recommendations_list = [{'objectID': row[0], 'title': row[1]} for row in rows]
    return recommendations_list
