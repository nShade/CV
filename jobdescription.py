from datetime import datetime, timedelta

from docutils.core import publish_doctree
from docutils.nodes import General, Element
from docutils.parsers.rst import directives, Directive

import rst2pdf.genelements as genelements
from reportlab.platypus import Table, Paragraph
from rst2pdf.image import MyImage


class JobEntryNode(General, Element):
    pass


class JobEtryDirective(Directive):
    has_content = True
    option_spec = {
        'icon': directives.unchanged,
        'company': directives.unchanged,
        'position': directives.unchanged,
        'start': directives.unchanged,
        'end': directives.unchanged,
        'responsibilities': directives.unchanged,
        'achievements': directives.unchanged,
    }

    def run(self):
        node = JobEntryNode()
        node['icon'] = self.options.get('icon', None)
        node['position'] = self.options.get('position', '')
        node['company'] = self.options.get('company', '')
        start = self.options.get('start', None)
        end = self.options.get('end', 'Present')

        startdate = datetime.strptime(start, '%b %Y')
        enddate = datetime.now() if end == 'Present' else datetime.strptime(end, '%b %Y')
        duration = ''
        years = enddate.year - startdate.year

        months = enddate.month - startdate.month + 1

        if months < 0:
            months = 12 + months
            years -= 1

        if years == 1:
            duration += f'{years} year'
        elif years > 1:
            duration += f'{years} years'

        if months != 0:
            if duration != '':
                duration += ' '

        if months == 1:
            duration += f'{months} month'
        elif months > 1:
            duration += f'{years} months'

        node['daterange'] = f'{start} - {end} ({duration})'
        node['responsibilities'] = self.options.get('responsibilities', None)
        node['achievements'] = self.options.get('achievements', None)
        return [node]


class JobEntryHandler(genelements.NodeHandler, JobEntryNode):

    def gather_elements(self, client, node, style):
        icon = MyImage(node['icon'], width=64, height=64, client=client)

        position = Paragraph(node['position'], client.styles['position'])
        company = Paragraph(node['company'], client.styles['company'])
        daterange = Paragraph(node['daterange'], client.styles['daterange'])

        description = client.gen_elements(
            publish_doctree(
                f".. class:: positiondescription\n"
                f"**Responsibilities**:\n\n"
                f"{node['responsibilities']}\n\n"
                f"**Achievements:**\n\n"
                f"{node['achievements']}\n",
                source_path='',
                settings_overrides={},
            )
        )

        t = Table(
            data=[[icon, position],
                  ['', company],
                  ['', daterange],
                  ['', description]],
            colWidths=(32, 600),
            hAlign='LEFT',
            vAlign='CENTER'
        )
        return [t]


directives.register_directive("jobentry", JobEtryDirective)
