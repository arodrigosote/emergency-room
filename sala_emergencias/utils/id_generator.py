def generate_visit_id(patient_id, doctor_id, emergency_room_id, visit_counter):
    return f"{patient_id}-{doctor_id}-{emergency_room_id}-{visit_counter}"
