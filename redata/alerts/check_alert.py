import pandas as pd
import json
from redata.db_operations import metrics_db, metrics_session

from redata.models.table import MonitoredTable
from redata.alerts.base import alert_on_z_score, get_last_results
from redata.models import Alert, Metric

from redata import settings

def alert(db, check, conf):
    if check.name == Metric.SCHEMA_CHANGE:
        alert_for_schema_change(db, check, conf)
    else:

        sql_df = get_last_results(db, check, conf)
        sql_df['result'] = pd.to_numeric(sql_df['result'])

        alert = check.name
        checked_txt = alert + ' is failing'

        alert_on_z_score(sql_df, check, alert, checked_txt, conf)


def alert_for_schema_change(db, check, conf):

    df = get_last_results(db, check, conf, days=1)
    for index, row in df.iterrows():

        changes = json.loads(row[0])
        if changes['operation'] == 'table detected':
            continue

        alert = Alert(
            text=f"""
                schema change detected - {changes['operation']}: {changes['column_name']}
            """,
            severity=2,
            table_id=check.table_id,
            alert_type=check.name,
            created_at=conf.for_time
        )

        metrics_session.add(alert)
        metrics_session.commit()


    
