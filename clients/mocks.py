from datetime import datetime

TEST_UPDATE_TIME = datetime.now()


def mock_perform_update(self, serializer):
    serializer.save(date_updated=TEST_UPDATE_TIME.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
