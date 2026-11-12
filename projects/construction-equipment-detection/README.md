# Construction Equipment Object Detection

**YOLOv5s 기반 건설중장비 객체 인식 시스템 **



## 프로젝트 개요

왜곡된 AVM(Around View Monitoring) 영상에서 사람 등 객체를 탐지하여 건설중장비 주변 상황을 파악하는 시스템을 주제로 한 캡스톤 프로젝트입니다.

### 원본 프로젝트에서 다룬 문제

- YOLOv5s를 활용한 객체 인식
- AVM 영상 왜곡으로 인한 탐지 난이도
- 그림자에 따른 오탐지
- 실시간 영상 스트리밍과 비동기 처리
- 서버–클라이언트 데이터 전달

### 이 예제의 구현 범위

- 로컬 영상 파일 또는 웹캠 입력
- **사용자가 별도로 제공하는** YOLOv5 형식 모델 가중치를 통한 객체 탐지
- 사람(person) 클래스 필터링
- 탐지 결과 바운딩 박스 표시 및 결과 영상 저장
- 탐지 결과 JSON Lines 로깅

**모델 가중치는 포함되지 않습니다.** 본 예제는 YOLOv5 호환 환경 및 모델 파일이 준비된 경우에만 추론할 수 있습니다. 학습·평가·실시간 서버 배포 기능은 구현하지 않았습니다.

## 구조

```text
construction-equipment-detection/
├── README.md
├── detect.py
├── requirements.txt
└── .gitignore
```

## 실행 방법

Python 3.10 이상, PyTorch 및 YOLOv5가 호환되는 환경을 준비하세요.

```bash
python -m pip install -r requirements.txt
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
python -m pip install -r requirements.txt
cd ..
python detect.py --weights path/to/best.pt --source path/to/avm_video.mp4 --yolov5-repo yolov5 --output result.mp4
```

웹캠은 `--source 0`으로 지정할 수 있습니다. 영상 처리는 모델과 컴퓨터 성능에 따라 느릴 수 있습니다.

> PyTorch Hub는 로컬 YOLOv5 저장소에서 코드를 로드합니다. 신뢰할 수 있는 저장소만 사용하세요.

## 기술 스택

Python · PyTorch · YOLOv5s · OpenCV · NumPy

## 포트폴리오 설명 시 유의사항

이 코드의 실행 여부, 정확도, 처리 속도는 실제 모델 가중치와 환경에 따라 달라집니다. 과거 프로젝트에서 언급된 탐지 재현율 등의 수치를 **이 예제의 검증 결과로 표시하지 않습니다.** 별도의 실험 기록 없이 수치를 주장하지 않습니다.

## 향후 개선

1. 원본 프로젝트의 전처리/왜곡 보정 코드 복원
2. AVM 영상 데이터셋과 평가 절차 정리
3. 그림자 오탐지 분석 및 증강 실험
4. 비동기 스트리밍 서버와 클라이언트 연결
5. FPS, 지연시간, Precision/Recall 측정

---

**Portfolio sample implementation** · 원본 캡스톤 산출물과 별개로 작성한 예제입니다.
