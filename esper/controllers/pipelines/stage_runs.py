from cement import Controller, ex
from clint.textui import prompt

from esper.controllers.enums import OutputFormat
from esper.ext.db_wrapper import DBWrapper
from esper.ext.pipelines_api import PipelinesApiAdapter
from esper.ext.utils import validate_creds_exists

class StageRuns(Controller):

    class Meta:
        label = 'stageruns'

        # text displayed at the top of --help output
        description = 'Stage runs'

        # text displayed at the bottom of --help output
        epilog = 'Usage: espercli pipelines stageruns'

        stacked_type = 'nested'
        stacked_on = 'runs'

    @ex(
        help='Show stage runs for a pipeline run',
        arguments=[
            (['-r', '--run-id'],
             {'help': 'pipeline run id',
              'action': 'store',
              'dest': 'run',
              'default': None}),
        ]
    )
    def show(self):
        validate_creds_exists(self.app)
        db = DBWrapper(self.app.creds)
        environment = db.get_configure().get("environment")
        auth_token = db.get_auth_token()
        adapter = PipelinesApiAdapter(environment, auth_token['auth_token'])

        pipeline = db.get_pipeline()
        if pipeline is None or pipeline.get('id') is None:
            self.app.log.debug('[pipeline-active] There is no active pipeline.')
            self.app.render('There is no active pipeline. Please set an active pipeline before getting a Stage')
            return

        run_id = self.app.pargs.run
        render_data = []

        if not run_id:
            run_id = input("Id of the Pipeline run: ")

        result = adapter.get_pipeline_run_stage_runs(run_id)
        result = result['content']['results']

        for stage_run in result:
            stage_render = {
                'Run Number': stage_run['run_number'],
                'Status': stage_run['status'],
                'Id': stage_run['id'],
                'Created At': stage_run['created_at'],
                }
            render_data.append(stage_render)

        self.app.render(f"Listing runs for the Pipeline! Details: \n")
        self.app.render(render_data, format=OutputFormat.TABULATED.value, headers="keys", tablefmt="plain")