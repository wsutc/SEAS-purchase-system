from tracking import create_tracker,update_tracker

tracker = create_tracker('fedex','574353194910','dcbad674-9232-4bd1-b3fb-eceac9cad026')

print(tracker['meta-code'])
print(tracker['link'])