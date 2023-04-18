import logging

logging.basicConfig(format="【%(asctime)s】-【%(levelname)s】: %(message)s",
                    datefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.DEBUG)

# from red_agent_lk_v1 import main_versus
from blue_agent_lj import main_versus
