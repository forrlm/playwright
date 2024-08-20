import re
from typing import Dict
from core.propertyResolver import PropertyResolver as P


@P.base
def pre_application(**kwargs: Dict | None) -> Dict:
    page = {
        "title": "application申请主页",
        "description": '',
        "properties": {
            'choose_loan_officer': {
                'loc': {
                    'get_by_text': 'Refinance my home',
                },
                'op': {
                    'click': '',
                },
                'next': {
                    'loc': {
                        'get_by_text': 'Yes'
                    },
                    'op': {
                        'click': '',
                    },
                    'next': {
                        'loc': {
                            'locator': 'div',
                            'filter': {
                                'has_text': re.compile(
                                    r"^Do you currently have a loan officer\?YesNoPlease select your loan officer$")
                            },
                            'loc': 'span',
                            'nth': 1,
                        },
                        'op': {
                            'click': None,
                        }
                    }
                },
            },
            'refinance_my_home': {
                # 'locator': {
                #     'by_text': 'Refinance my home',
                # },
                'operation': {
                    'click': r'text="Refinance my home"',
                },
                'next': {
                    'loc': {
                        'locator': '.check-group-box-l > .circle',
                        'first': None,
                    },
                    'op': {
                        'click': ''
                    },
                    'next': {
                        'loc': {
                            'locator': 'div',
                            'filter': {
                                'has_text': re.compile(
                                    r"^Do you currently have a loan officer\?YesNoPlease select your loan officer$")
                            },
                            'loc': 'span',
                            'nth': 1,
                        },
                        'op': {
                            'click': '',
                        },
                        'next': {
                            'loc': {
                                'get_by_text': "Yingjie Yu(yingjie@zeitro.com)",
                            },
                            'op': {
                                'click': '',
                            },
                            'next': {
                                'loc': {
                                    'get_by_role': {
                                        'role': 'button',
                                        'name': 'next step'
                                    },
                                },
                                'op': {
                                    'click': '',
                                },
                                'next': {
                                    'loc': {
                                        'get_by_placeholder': 'Enter your email address'
                                    },
                                    'op': {
                                        'fill': 'langran@zeitro.comzeitro'
                                    },
                                    'next': {
                                        'loc': {
                                            'get_by_role': {
                                                'role': 'button',
                                                'name': 'continue'
                                            },
                                        },
                                        'op': {
                                            'click': '',
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return locals()
