import time
import pandas
from copy import deepcopy as copy
from pypresto import PrestoConnection


class Py3PrestoConnection(PrestoConnection):

    def run_query(self,sql_query,ignore_empty=False) :
        response = self.send_query(sql_query)
        series = []
        columns = []
        while 'nextUri' in response :
            response = self.make_request(response['nextUri'])
            if 'data' in response :
                columns = columns or [col['name'] for col in response['columns']]
                lst_rows = response['data']
                for row in lst_rows:
                    serie = {}
                    for idx in range(len(columns)):
                        serie[columns[idx]] = row[idx]
                    series.append(copy(serie))
                #print 'Getting data (rows: %s)' % len(series)
                time.sleep(1)
            elif 'columns' in response :
                columns = columns or [col['name'] for col in response['columns']]
            else:
                #print 'Running query'
                time.sleep(5)
        df = pandas.DataFrame(series,columns=columns)
        if df.empty and not ignore_empty :
            raise Exception('No data returned')
        return df

