class queries:
   def signin():
       return '''
       mutation ($username: String!, $password: String!, $rememberme: Boolean) {
           signinByUsername (username: $username, password: $password, rememberme: $rememberme) {
               id
               username
               nickname
           }
       }
       '''
   def cloud_server_info():
       return '''
       query GET_CLOUD_SERVER_INFO($id: ID!) {
           cloudServerInfo(id: $id) {
               url
               query
           }
       }
       '''
   def create_entry_story():
       return '''
       mutation CREATE_ENTRYSTORY(
           $content: String
           $text: String
           $image: String
           $sticker: ID
           $stickerItem: ID
           $cursor: String
       ) {
           createEntryStory(
               content: $content
               text: $text
               image: $image
               sticker: $sticker
               stickerItem: $stickerItem
               cursor: $cursor
           ) {
               warning
               discuss {
                   id
                   title
                   content
                   seContent
                   created
                   commentsLength
                   likesLength
                   favorite
                   visit
                   category
                   prefix
                   groupNotice
                   user {
                       id
                       nickname
                       username
                       profileImage {
                           id
                           name
                           label {
                               ko
                               en
                               ja
                               vn
                           }
                           filename
                           imageType
                           dimension {
                               width
                               height
                           }
                           trimmed {
                               filename
                               width
                               height
                           }
                       }
                       status {
                           following
                           follower
                       }
                       description
                       role
                       mark {
                           id
                           name
                           label {
                               ko
                               en
                               ja
                               vn
                           }
                           filename
                           imageType
                           dimension {
                               width
                               height
                           }
                           trimmed {
                               filename
                               width
                               height
                           }
                       }
                   }
                   images {
                       filename
                       imageUrl
                   }
                   sticker {
                       id
                       name
                       label {
                           ko
                           en
                           ja
                           vn
                       }
                       filename
                       imageType
                       dimension {
                           width
                           height
                       }
                       trimmed {
                           filename
                           width
                           height
                       }
                   }
                   progress
                   thumbnail
                   reply
                   bestComment {
                       id
                       user {
                           id
                           nickname
                           username
                           profileImage {
                               id
                               name
                               label {
                                   ko
                                   en
                                   ja
                                   vn
                               }
                               filename
                               imageType
                               dimension {
                                   width
                                   height
                               }
                               trimmed {
                                   filename
                                   width
                                   height
                               }
                           }
                           status {
                               following
                               follower
                           }
                           description
                           role
                           mark {
                               id
                               name
                               label {
                                   ko
                                   en
                                   ja
                                   vn
                               }
                               filename
                               imageType
                               dimension {
                                   width
                                   height
                               }
                               trimmed {
                                   filename
                                   width
                                   height
                               }
                           }
                       }
                       content
                       created
                       removed
                       blamed
                       blamedBy
                       commentsLength
                       likesLength
                       isLike
                       hide
                       pinned
                       image {
                           id
                           name
                           label {
                               ko
                               en
                               ja
                               vn
                           }
                           filename
                           imageType
                           dimension {
                               width
                               height
                           }
                           trimmed {
                               filename
                               width
                               height
                           }
                       }
                       sticker {
                           id
                           name
                           label {
                               ko
                               en
                               ja
                               vn
                           }
                           filename
                           imageType
                           dimension {
                               width
                               height
                           }
                           trimmed {
                               filename
                               width
                               height
                           }
                       }
                   }
                   blamed
                   description1
                   description2
                   description3
                   tags
               }
           }
       }
       '''