from module.SiteTemplate import SiteTemplate


class SiteTemplateService(object):
    def __init__(self):
        self.site_template_db = SiteTemplate()

    def get_template_list(self, state, template_type):
        return self.site_template_db.get_template_list(state, template_type)
