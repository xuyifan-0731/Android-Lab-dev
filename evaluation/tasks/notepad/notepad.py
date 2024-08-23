from evaluation.task import *


class SingleTask_Notepad_1(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 判断是否包含 "Contact" 和 "John"
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree, "Share") and find_subtrees_of_parents_with_key(
                xml_compressed_tree, "Quick insert")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Meeting")
        outcome = {"judge_page": True, "1": False, "complete": False}

        if (len(outs) > 0):
            outcome["1"] = True
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_2(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree, "Share") and find_subtrees_of_parents_with_key(
                xml_compressed_tree, "Quick insert")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Concert")
        # print(outs)
        outcome = {"judge_page": True, "1": False, "2": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
        outs = find_matching_subtrees(xml_compressed_tree, "ScrollView")
        for out in outs:
            for key, value in out.items():
                for key2, value2 in value.items():
                    if ('14 p.m. at building no.1' in key2):
                        outcome["2"] = True
            # print(out)
        if (outcome["1"] and outcome["2"]):
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_3(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                  "New item") and find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                                                                    "Search & sort")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "To do list")
        outcome = {"judge_page": True, "1": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_4(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                  "New item") and find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                                                                    "Search & sort")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "To do list")
        outcome = {"judge_page": True, "1": False, "2": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "check ; unchecked ;;Eggs")
        if (len(outs) > 0):
            outcome["2"] = True
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "check ; checked ;;Eggs")
        if (len(outs) > 0):
            outcome["2"] = True
        if (outcome["1"] and outcome["2"]):
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_5(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                  "Import checklist") and find_subtrees_of_parents_with_key(
            xml_compressed_tree, "File encoding")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Import checklist")
        outcome = {"judge_page": True, "1": False, "complete": False}

        for out in outs:
            for key, value in out.items():
                for key2, value2 in value.items():
                    if "unchecked" in key2:
                        outcome["1"] = True
                        break

        if (outcome["1"]):
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_6(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree, "Share") and find_subtrees_of_parents_with_key(
                xml_compressed_tree, "Quick insert")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Meeting")
        # print(outs)
        outcome = {"judge_page": True, "1": False, "2": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
        outs = find_matching_subtrees(xml_compressed_tree, "ScrollView")
        for out in outs:
            for key, value in out.items():
                for key2, value2 in value.items():
                    if ('Tommorrow' in key2):
                        outcome["2"] = True
            # print(out)
        if (outcome["1"] and outcome["2"]):
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_7(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree, "Search") and find_subtrees_of_parents_with_key(
                xml_compressed_tree, "CLEAR")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Meeting")
        outcome = {"judge_page": True, "1": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_8(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                  "Add quick insert item") and find_subtrees_of_parents_with_key(
            xml_compressed_tree, "CANCEL")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "alice")
        outcome = {"judge_page": True, "1": False, "complete": False}

        if (len(outs) > 0):
            outcome["1"] = True
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_9(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                  "Repeat every 5 minutes") and find_subtrees_of_parents_with_key(
            xml_compressed_tree, "Notification sound")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Repeat every 5 minutes")
        outcome = {"judge_page": True, "1": False, "complete": False}

        for out in outs:
            for key, value in out.items():
                for key2, value2 in value.items():
                    if ('checked' in key2 and (not 'unchecked' in key2)):
                        outcome["1"] = True
                        break

        if outcome["1"] == True:
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_10(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree, "Settings/Tools")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outcome = {"judge_page": True, "1": False, "complete": False}
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Remember last sorting")
        for out in outs:
            for key, value in out.items():
                for key2, value2 in value.items():
                    if ('checked' in key2 and (not 'unchecked' in key2)):
                        outcome["1"] = True
                        break

        if outcome["1"] == True:
            outcome["complete"] = True
        return outcome


class SingleTask_Notepad_11(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree, "Share") and find_subtrees_of_parents_with_key(
                xml_compressed_tree, "Quick insert")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "Work")
        # print(outs)
        outcome = {"judge_page": True, "1": False, "2": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
        outs = find_matching_subtrees(xml_compressed_tree, "ScrollView")
        for out in outs:
            for key, value in out.items():
                for key2, value2 in value.items():
                    if ('Due tommorrow' in key2):
                        outcome["2"] = True
            # print(out)
        if (outcome["1"] and outcome["2"]):
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_12(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                  "New item") and find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                                                                    "Search & sort")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "To do list")
        outcome = {"judge_page": True, "1": False, "2": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "check ; unchecked ;;Enrollment")
        if (len(outs) > 0):
            outcome["2"] = True
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "check ; checked ;;Enrollment")
        if (len(outs) > 0):
            outcome["2"] = True
        if (outcome["1"] and outcome["2"]):
            outcome["complete"] = True

        return outcome


class SingleTask_Notepad_13(SingleTask):

    def judge_page(self, xml_compressed_tree):
        # 可以根据需要在这里实现特定的页面判断逻辑
        if not (find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                  "New item") and find_subtrees_of_parents_with_key(xml_compressed_tree,
                                                                                                    "Search & sort")):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}

        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "To do list")
        outcome = {"judge_page": True, "1": False, "2": False, "complete": False}
        if (len(outs) > 0):
            outcome["1"] = True
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "check ; checked ;;Eggs")
        if (len(outs) > 0):
            outcome["2"] = True
        if (outcome["1"] and outcome["2"]):
            outcome["complete"] = True

        return outcome
