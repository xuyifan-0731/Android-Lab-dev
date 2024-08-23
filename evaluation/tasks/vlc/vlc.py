from evaluation.task import *


def check_sorted_desc(xml_compressed_tree):
    Vlist = find_matching_subtrees(xml_compressed_tree, "Video:")
    video_list = [next(iter(Vdict)) for Vdict in Vlist]

    def extract_duration(text):
        match = re.search(r'Duration: (\d+) minutes (\d+) seconds', text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds
        else:
            return 0

    durations = [extract_duration(item) for item in video_list]
    is_sorted_desc = all(durations[i] >= durations[i + 1] for i in range(len(durations) - 1))
    return is_sorted_desc


class SingleTask_vlc_1(SingleTask):

    def judge_page(self, line):
        if line["parsed_action"]["action"] != "finish":
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(line):
            return {"judge_page": False}

        answer = "3 videos in total"
        self.save_answer(answer)
        if self.check_answer(line):
            outcome = {"judge_page": True, "1": True, "complete": True}
        else:
            outcome = {"judge_page": True, "1": False, "complete": False}
        return outcome


class SingleTask_vlc_2(SingleTask):

    def judge_page(self, line):
        if line["parsed_action"]["action"] != "finish":
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(line):
            return {"judge_page": False}

        answer = "11 minutes and 44 seconds"
        self.save_answer(answer)
        if self.check_answer(line):
            outcome = {"judge_page": True, "1": True, "complete": True}
        else:
            outcome = {"judge_page": True, "1": False, "complete": False}
        return outcome


class SingleTask_vlc_3(SingleTask):

    def judge_page(self, line):
        if line["parsed_action"]["action"] != "finish":
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(line):
            return {"judge_page": False}

        answer = "1280x720 and 2160x900 respectively"
        self.save_answer(answer)
        if self.check_answer(line):
            outcome = {"judge_page": True, "1": True, "complete": True}
        else:
            outcome = {"judge_page": True, "1": False, "complete": False}
        return outcome


class SingleTask_vlc_4(SingleTask):

    def judge_page(self, line):
        if line["parsed_action"]["action"] != "finish":
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(line):
            return {"judge_page": False}

        answer = "Yes"
        self.save_answer(answer)
        if self.check_answer(line):
            outcome = {"judge_page": True, "1": True, "complete": True}
        else:
            outcome = {"judge_page": True, "1": False, "complete": False}
        return outcome


class SingleTask_vlc_5(SingleTask):

    def judge_page(self, line):
        if line["parsed_action"]["action"] != "finish":
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(line):
            return {"judge_page": False}

        answer = "125.38 MB"
        self.save_answer(answer)
        if self.check_answer(line):
            outcome = {"judge_page": True, "1": True, "complete": True}
        else:
            outcome = {"judge_page": True, "1": False, "complete": False}
        return outcome


class SingleTask_vlc_6(SingleTask):

    def judge_page(self, xml_compressed_tree):
        player_dict = find_matching_subtrees(xml_compressed_tree, "Video player")[0]
        player = next(iter(player_dict))
        return "Video player" in player

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        try:
            video_dict = find_matching_subtrees(xml_compressed_tree, "TextView")[-1]
            play_dict = find_matching_subtrees(xml_compressed_tree, "ImageView")[-1]
            video = next(iter(video_dict))
            play = next(iter(play_dict))
        except:
            return {"judge_page": False}

        judge_video = judge_pause = False
        judge_video = "Mikaela Shiffrin @ LSC 1 30 16" in video
        judge_pause = "Play" in play

        return {
            "judge_page": True,
            "1": judge_video,
            "2": judge_pause,
            "complete": judge_video & judge_pause
        }


class SingleTask_vlc_7(SingleTask):

    def judge_page(self, xml_compressed_tree):
        try:
            selected = find_matching_subtrees(xml_compressed_tree, "focusable ; selected")[0]
        except:
            return False
        return "Video" in next(iter(selected))

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        judge_sorted_desc = check_sorted_desc(xml_compressed_tree)
        return {
            "judge_page": True,
            "1": judge_sorted_desc,
            "complete": judge_sorted_desc
        }
