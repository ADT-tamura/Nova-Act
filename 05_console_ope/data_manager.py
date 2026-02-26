"""JSONファイル操作とデータクラス"""
import json
from typing import Dict, List
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class NovaActInfo:
    """NovaActの基本情報を格納するデータクラス"""
    overview: str = ""
    features: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    additional_info: str = ""


@dataclass
class CaseStudy:
    """事例情報を格納するデータクラス"""
    title: str
    summary: str
    url: str
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ResearchData:
    """調査データ全体を管理するデータクラス"""
    nova_act_info: NovaActInfo = field(default_factory=NovaActInfo)
    case_studies: List[CaseStudy] = field(default_factory=list)
    research_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "research_date": self.research_date,
            "nova_act_info": asdict(self.nova_act_info),
            "case_studies": [asdict(cs) for cs in self.case_studies]
        }
    
    def save_to_json(self, filename: str = "nova_act_research.json"):
        """JSONファイルに保存（上書き方式）"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"\n💾 データを保存しました: {filename}")
    
    @classmethod
    def load_from_json(cls, filename: str = "nova_act_research.json") -> 'ResearchData':
        """JSONファイルから読み込み"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        research_data = cls()
        research_data.research_date = data.get("research_date", "")
        
        # NovaActInfoを復元
        nova_info_data = data.get("nova_act_info", {})
        research_data.nova_act_info = NovaActInfo(
            overview=nova_info_data.get("overview", ""),
            features=nova_info_data.get("features", []),
            use_cases=nova_info_data.get("use_cases", []),
            additional_info=nova_info_data.get("additional_info", "")
        )
        
        # CaseStudyを復元
        case_studies_data = data.get("case_studies", [])
        research_data.case_studies = [
            CaseStudy(**cs) for cs in case_studies_data
        ]
        
        return research_data
