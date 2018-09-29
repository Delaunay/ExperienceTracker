
from flask import Flask
import pandas as pd
import logging
import base64

import experience_tracker.database as database
import experience_tracker.template as html
import experience_tracker.fakefile as fakefile

ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
FLOAT_COLS = ['Time(%)', 'Time', 'Calls', 'Avg', 'Min', 'Max']
SELECTED_COLS = ['Name', 'Time(%)', 'Time', 'Calls', 'Avg', 'Min', 'Max']
SELECTED_COLS_COMP = ['Name', 'Job', 'Time(%)', 'Time', 'Calls', 'Avg', 'Min', 'Max']

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

app = Flask(__name__)
db = database.ExperienceDatabase()


def make_cpu_info(cpus):
    cpus = [html.list_item('{} - {} - (cores={})'.format(cpu[1], cpu[2], cpu[0])) for cpu in cpus]
    return html.unordered_list(cpus)


def make_gpu_info(gpus):
    gpus = [html.list_item('{} - (device_id={})'.format(gpu[1], gpu[0])) for gpu in gpus]
    return  html.unordered_list(gpus)


def make_memory_info(memory):
    return html.unordered_list([
        html.list_item('Avail: {:4.2f} Mio'.format(memory[0] / (1024 * 1024))),
        html.list_item('Free: {:4.2f} Mio'.format(memory[1] / (1024 * 1024)))
    ])


def make_system_info(cpu, gpu, memory, hostname):
    return html.unordered_list([
        html.list_item('CPU', make_cpu_info([cpu])),
        html.list_item('GPU:', make_gpu_info(gpu)),
        html.list_item('Memory', make_memory_info(memory)),
        html.list_item('Hostname {}'.format(hostname))
    ])


def html_reports(report, cols):
    gpu = report[report['Type'] == 'GPU activities']
    api = report[report['Type'] != 'GPU activities']
    gpu_html = gpu[cols].to_html(
        classes='table table-striped table-hover table-condensed table-dark',
        float_format=lambda x: '{:.4f}'.format(x), index=False)
    api_html = api[cols].to_html(
        classes='table table-striped table-hover table-condensed table-dark',
        float_format=lambda x: '{:.4f}'.format(x), index=False)

    return gpu_html, api_html


def make_reports_section(reports, date):
    sections = []
    for file_name, rep in reports.items():
        nvprof_header = rep['nvprof_header']
        csv = pd.read_csv(fakefile.FakeFile(rep['csv']), index_col=False)

        gpu_html, api_html = html_reports(csv, SELECTED_COLS)

        section = """
            <ul>
                <li>report file: {}</li>
                <li>date: {}</li>
            </ul>
            <pre class="bg-secondary">{}</pre>
            <h4>GPU Activities</h4>
            {}
            <h4>API calls</h4>
            {}
        """.format(file_name, date, ''.join(nvprof_header), gpu_html, api_html)
        sections.append(section)
    return sections


def base64encode(string: str) -> str:
    return base64.b64encode(string.encode('utf8')).decode('utf-8')


def make_compare_links(jb) -> str:
    b64_name = base64encode(jb['name'])
    page = ''
    if 'machines' in jb:
        machines = jb['machines']
        items = [html.list_item(html.link('compare/{}/{}'.format(b64_name, m), m)) for m in set(machines)]
        page = html.unordered_list(items)
    return page


@app.route('/')
def index() -> str:
    jobs = db.programs()
    job_list = []
    for program in jobs:
        link_name = '{} - {}'.format( program['name'], ' '.join(program['arguments']))
        link_url = '/job/{}'.format(program['uid'])
        job_list.append(
            html.list_item(
                html.link(link_name, link_url),
                make_compare_links(program)
            )
        )

    return html.make_page('<ul>{}</ul>'.format('\n'.join(job_list) ))


def optional_map(item, fun):
    if item is not None:
        return fun(item)
    return item


@app.route('/job/<uid>')
def job(uid: str) -> str:
    benchmarks = db.get_observation(by='program_uid', value=uid)

    if len(benchmarks) == 0:
        return html.make_page('no job with (uid={})'.format(uid))

    job_ref = db.get_program(by='uid', value=uid)[0]
    benchmarks = benchmarks[0]['obs']

    bench_mark_pages = []
    for bench in benchmarks:
        date = bench['date']
        system = bench['system']
        reports = bench['reports']
        output = bench.get('stdout')
        outerr = bench.get('stderr')

        page = """<h2>{} {}</h2>
            <h3>System</h3>
            {}
            <h3>stdout</h3>
            <pre class="bg-secondary">{}</pre>
            <h3>stderr</h3>
            <pre class="bg-secondary">{}</pre>
            <h3>Reports</h3>
            {}
        """.format(
            job_ref['name'], ' '.join(job_ref['arguments']),
            make_system_info(system['cpu'], system['gpu'], system['memory'], system['hostname']),
            optional_map(output, lambda x: ''.join(x)),
            optional_map(outerr, lambda x: ''.join(x)),
            '\n'.join(make_reports_section(reports, date))
        )

        bench_mark_pages.append(page)

    return html.make_page('\n'.join(bench_mark_pages))


def safe_convert(x: str) -> float:
    try:
        return float(x)
    except:
        return 0


@app.route('/compare/<name>/<hostname>')
def compare(name: str, hostname: str) -> str:
    name = base64.b64decode(name).decode('utf-8')
    print('Looking for {} ran on {}'.format(name, hostname))
    job_refs = db.get_program(by='name', value=name)

    if len(job_refs) == 0:
        return job(job_refs['uid'])

    for i in job_refs:
        print('Found job: {}'.format(i))

    #
    #   Database need to be reworked this is too messy
    #
    benchmarks = [db.get_observation(by='program_uid', value=j['uid']) for j in job_refs]
    benchmarks = list(filter(lambda x: len(x) > 0, benchmarks))
    benchmarks = [b[0] for b in benchmarks]

    if len(benchmarks) == 0:
        return 'No jobs found'

    comp_report = []
    job_link = {}

    for b, a in zip(benchmarks, ALPHA):
        # try to use the latest report
        reports = b['obs']
        reports = [x for x in reports if x['system']['hostname'] == hostname]
        print('{}'.format(len(reports)))
        reports = reports[-1]['reports']

        # usually only one report is generated by NVIDIA but this could change with MP
        data = {}
        for k, val in reports.items():
            data = val

        try:
            df = pd.read_csv(fakefile.FakeFile(data['csv']))
            df['Job'] = a
            comp_report.append(df)
            job_link[a] = {'uid': b['uid']}
            job_ref = db.get_program(by='uid', value=b['uid'])[0]
            job_link[a]['arguments'] = job_ref['arguments']
        except:
            print('Was not able to read CSV back for {}'.format(a))

    total = pd.concat(comp_report, ignore_index=True)

    for col in FLOAT_COLS:
        total[col] = total[col].apply(safe_convert)

    total = total.sort_values(by=['Time(%)'], ascending=False)

    job_description = [
        '<li>{} | {} | {}</li>'.format(job_ref['uid'], key, ' '.join(job_ref['arguments']))
            for key, job_ref in job_link.items()
    ]

    gpu_html, api_html = html_reports(total, SELECTED_COLS_COMP)

    page = """
        <h1> Jobs </h1>
        
        <ul>
            <li>Name: {}</li>
            <li>Machine: {}</li>
        </ul>
        <ul>{}</ul>
        
        <h1>GPU Activities</h1>
        {}
        <h1>API Calls </h1>
        {}
    """.format(name, hostname, ''.join(job_description), gpu_html, api_html)

    return html.make_page(page)



