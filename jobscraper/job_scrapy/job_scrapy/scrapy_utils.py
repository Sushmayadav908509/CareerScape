import json

def extract_job_info(json_data):
    job_info = {
        "job_title": json_data.get("title", ""),
        "company_name": json_data.get("hiringOrganization", {}).get("name", ""),
        "company_location": json_data.get("jobLocation", {}).get("address", {}).get("addressLocality", ""),
        "job_description": json_data.get("description", ""),
        "datePosted": json_data.get("datePosted", "")[:10],
    }

    employment_type = json_data.get("employmentType", [])
    if employment_type:
        job_info["job_types"] = ', '.join(employment_type)
    else:
        job_info["job_types"] = None


    if "baseSalary" in json_data:
        base_salary = json_data["baseSalary"]
        job_info["min_salary"] = base_salary.get("value", {}).get("minValue", "")
        job_info["max_salary"] = base_salary.get("value", {}).get("maxValue", "")
        job_info["salary_unit"] = base_salary.get("value", {}).get("unitText", "")

    return job_info