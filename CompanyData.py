class CompanyData(object):
    def __init__(self, initials, name, infomoney_url, company_type, sector, description):
        self.initials = initials
        self.name = name
        self.infomoney_url = infomoney_url
        self.company_type = company_type
        self.sector = sector
        self.description = description

    def to_map(self):
        return {
            'initials': self.initials,
            'name': self.name,
            'infomoneyUrl': self.infomoney_url,
            'type': self.company_type,
            'sector': self.sector,
            'description': self.description,
        }
