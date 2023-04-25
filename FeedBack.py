def FindAndExtract(response):
    # Deifne this based on your field target. 
    MatchString = b"\x55\xcd"
    MatchIndex = response.find(MatchString)
    SplicedResponse = None

    if MatchIndex != -1:
        SplicedResponse = response[MatchIndex:]
    return SplicedResponse