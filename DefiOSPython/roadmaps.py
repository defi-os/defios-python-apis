from models import Roadmap
from authentication import validate_user
from flask import jsonify, make_response
import json

def get_roadmaps(token, request_params):
    """
    Used to fetch roadmaps given one or more set of filters
    
    Parameters
    --------------------
    token:string
                  Unique jwt identifier of the user
    request_params:json
                    Set of filters to be applied to data, the available filters are:
                       1) filter.roadmap_total_stake
                       2) filter.roadmap_active_objectives
                       3) filter.roadmap_outlook
                       4) filter.roadmap_outcome_types
                       5) search.roadmap_creator_gh_name
                       6) search.roadmap_title

    Returns
    --------------------
    issues -> List[Issues]:
            Return list of Roadmaps model raw json of the flitered roadmaps
    
    """
    isAuthorized, resp = validate_user(token)
    if not isAuthorized:
        return resp
    try:
        search_params = {
            i.split("search.")[1]: request_params[i]
            for i in request_params if "search" in i and request_params[i] != ""
        }

        if search_params.get("roadmap_creator_gh_name", False):
            search_params["roadmap_creator_gh_name"] = {
                "$regex": search_params["roadmap_creator_gh_name"]
            }
        
        if search_params.get("roadmap_title", False):
            search_params["roadmap_title"] = {
                "$regex": search_params["roadmap_title"]
            }

        filter_params = {
            i.split("filter.")[1]: request_params[i]
            for i in request_params if "filter" in i and request_params[i] != ""
        }

        for filter_param in filter_params:
            if filter_param == "roadmap_total_stake":
                filter_params["roadmap_total_stake"] = {
                    "$gte": float(filter_params["roadmap_total_stake"].split(",")[0]),
                    "$lt": float(filter_params["roadmap_total_stake"].split(",")[1])
                }
            
            elif filter_param == "roadmap_active_objectives":
                filter_params["roadmap_active_objectives"] = {
                    "$gte": float(filter_params["roadmap_active_objectives"].split(",")[0]),
                    "$lt": float(filter_params["roadmap_active_objectives"].split(",")[1])                    
                }
            
            else:
                filter_params[filter_param] = {
                    "$in": filter_params[filter_param].split(",")
                }

        roadmaps = Roadmap.objects(
            __raw__= search_params | filter_params
        ).exclude(
            "roadmap_objectives_list", "roadmap_objectives_graph"
        ).all()
        message = [i.to_roadmap_json() for i in roadmaps]
        status_code = 200
    except Exception:
        message = {"error": "FetchRoadmapsFailed"}
        status_code = 400
    return make_response(jsonify(message), status_code)