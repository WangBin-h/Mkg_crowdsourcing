import redis
from redisgraph import Graph, Node, Edge
from django.conf import settings

# Redis 连接
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

# RedisGraph 连接
graph = Graph(settings.REDIS_GRAPH_NAME, redis_client)

def get_medical_org_by_id(org_id):
    """
    从 Redis 获取医疗机构的详细信息
    """
    return redis_client.hgetall(org_id)

def get_medical_orgs_by_category(category):
    """
    获取指定类别的医疗机构
    """
    org_ids = redis_client.smembers(f'category:{category}')
    return [redis_client.hgetall(org_id) for org_id in org_ids]

def get_graph_data():
    """
    获取 RedisGraph 中的图数据
    """
    query = "MATCH (n) RETURN n"
    result = graph.query(query)
    return [record[0].properties for record in result.result_set]
