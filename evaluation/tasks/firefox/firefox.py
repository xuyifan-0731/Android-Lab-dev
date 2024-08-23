from evaluation.task import *


class SingleTask_Firefox_1(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "m.facebook.com"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        return {"judge_page": True, "1": True, "complete": True}


class SingleTask_Firefox_2(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "m.youtube.com"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        return {"judge_page": True, "1": True, "complete": True}


class SingleTask_Firefox_3(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "m.wikipedia.org"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        return {"judge_page": True, "1": True, "complete": True}


class SingleTask_Firefox_4(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "q=apple"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        return {"judge_page": True, "1": True, "complete": True}


class SingleTask_Firefox_5(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "m.baidu.com"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        return {"judge_page": True, "1": True, "complete": True}


class SingleTask_Firefox_6(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "q=national+day"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        return {"judge_page": True, "1": True, "complete": True}


class SingleTask_Firefox_7(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "m.jd.com"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        return {"judge_page": True, "1": True, "complete": True}


class SingleTask_Firefox_8(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "baidu.com"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        key = True
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "word=match")
        if (len(outs) == 0):
            key = False
        return {"judge_page": True, "1": key, "complete": key}


class SingleTask_Firefox_9(SingleTask):

    def judge_page(self, xml_compressed_tree):
        if not find_subtrees_of_parents_with_key(xml_compressed_tree, "m.jd.com"):
            return False
        return True

    def judge(self, xml_compressed_tree, line):
        if not self.judge_page(xml_compressed_tree):
            return {"judge_page": False}
        key = True
        outs = find_subtrees_of_parents_with_key(xml_compressed_tree, "keyword=dress")
        if (len(outs) == 0):
            key = False
        return {"judge_page": True, "1": key, "complete": key}
