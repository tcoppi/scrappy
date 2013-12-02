from module import Module, DBModel

class skeleton(Module):

    def __init__(self, scrap):
        super(skeleton, self).__init__(scrap)
        scrap.register_event("skeleton", "msg", self.distribute)

        self.register_cmd("skeleton", self.warn)

    def warn(self, server, event, bot):
        self.logger.warn("Skeleton module is intended as a skeleton module only. Don't actually use it.")
