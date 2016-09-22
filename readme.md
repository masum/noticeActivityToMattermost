## 概要
GitLabのCommitとMergeRequestをMattermostへ通知。  
  
GitLabにはWebHook機能があるが、GitLabの利用バージョンが古かったり、新しくてもWebHookが利用できない環境の場合がある。
そういうケースでもMattermostへ通知できるように、ポーリングして新しいCommitやMergeRequestを検知する。  

起動した場所に、{プロジェクト名}.txt というファイルが作成され、そこに「最終チェック日時」を保存している。その日付以降のCommitとMergeRequestを通知する仕組み。  
そのため、定期実行そのものは、cloneやJenkinsなどで設定する事を想定している。  

### 呼び出し方法

ヘルプ
```
python app.py -h 
```

以下の情報をパラメタで、以下の順番で指定する
* GitLabのURL
* GitLabのプロジェクト名
* GitLabのグループ名
* GitLabのログインID
* GitLabのパスワード
* Mattermostに投稿する際のアイコン(画像)のURL
* Mattermostのincoming URL

