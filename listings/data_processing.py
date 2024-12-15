# JobHub\listings\data_processing.py
import locale

def format_salary(salary):
    if isinstance(salary, (float, int)):
        locale.setlocale(locale.LC_ALL, 'en_IN')
        formatted_salary = locale.format_string('%f', salary, grouping=True)
        parts = formatted_salary.split('.')
        if len(parts) == 2:
            # return f"{parts[0]}.{parts[1][0]}"
            return parts[0]
        else:
            return formatted_salary
    else:
        return str(salary)
    

def format_job_type(job_type):
    if job_type is None:
        return None
    
    job_type_list = job_type.split(', ')

    if 'OTHER' in job_type_list:
        job_type_list.remove('OTHER')
    
    formatted_types = [type.replace('_', ' ') for type in job_type_list]
    return ', '.join(formatted_types)

def format_salary_unit(salary_unit):
    return salary_unit.capitalize()