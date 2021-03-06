class User:
    def __init__(self, api_dict):
        self.user_id = api_dict['user_id']
        self.username = api_dict['username']
        self.join_date = api_dict['join_date']
        self.count300 = api_dict['count300']
        self.count100 = api_dict['count100']
        self.count50 = api_dict['count50']
        self.playcount = api_dict['playcount']
        self.ranked_score = api_dict['ranked_score']
        self.total_score = api_dict['total_score']
        self.pp_rank = api_dict['pp_rank']
        self.level = api_dict['level']
        self.pp_raw = api_dict['pp_raw']
        self.accuracy = api_dict['accuracy']
        self.count_rank_ss = api_dict['count_rank_ss']
        self.count_rank_ssh = api_dict['count_rank_ssh']
        self.count_rank_s = api_dict['count_rank_s']
        self.count_rank_sh = api_dict['count_rank_sh']
        self.count_rank_a = api_dict['count_rank_a']
        self.country = api_dict['country']
        self.total_seconds_played = api_dict['total_seconds_played']
        self.pp_country_rank = api_dict['pp_country_rank']
        self.events = api_dict['events']