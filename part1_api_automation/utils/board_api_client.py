import requests

class BoardApiClient:
    def __init__(self, token):
        # 기본 URL 설정
        self.base_url = "https://api-rest.elice.io/org/qatrack/board/article"
        self.classroom_url = "https://api-classroom.elice.io/classroom/a6bd98a3-83ff-4e5d-ba9e-6c04c69592fc/article"
        self.session = requests.Session()
        # 헤더에 토큰 설정
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_article_list(self, board_id=9307, offset=0, count=15):
        """게시글 목록 조회 API"""
        params = {
            "board_id": board_id,
            "offset": offset,
            "count": count
        }
        # GET https://api-rest.elice.io/org/qatrack/board/article/list/ 호출
        return self.session.get(f"{self.base_url}/list/", params=params)
    
    def get_classroom_articles(self, filter_title="%%", sort_by="created_desc", skip=0, count=10):
        """게시글 조회 API (정렬 검증용)"""
        params = {
            "filter_title": filter_title,
            "sort_by": sort_by,
            "skip": skip,
            "count": count
        }
        return self.session.get(self.classroom_url, params=params)